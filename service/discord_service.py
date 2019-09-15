from service.file_service import FileService
from datetime import datetime, timedelta
import operator
import discord
import asyncio
import random


class DiscordService(object):
    def __init__(self, client):
        super().__init__()
        self.file_service = FileService()
        self.settings = self.file_service.load_json_file("resources/settings.json")
        self.command_texts = self.file_service.load_json_file("resources/command_texts.json")
        self.responses = self.file_service.load_json_file("resources/responses.json")
        self.filters = self.file_service.load_json_file("resources/filters.json")
        self.client = client

    def list_first_members(self, guild):
        memberstime = {}
        for member in guild.members:
            if member.nick:
                memberstime[member.nick] = member.joined_at
            else:
                memberstime[member.name] = member.joined_at
        members = sorted(memberstime.items(), key=operator.itemgetter(1))
        lst_members = ["%s - %s" % (name, time.strftime("%d/%m/%Y - %H:%M:%S")) for name, time in members]
        for i, member in enumerate(lst_members):
            lst_members[i] = "%s. %s" % (i + 1, lst_members[i])
        return lst_members

    def create_bot_message(self, args, user):
        chan = self.client.get_channel(int(args[0]))
        msg = " ".join(args[1:])
        asyncio.get_event_loop().create_task(chan.send(msg))

        embed = self.create_embedded_action_logs("!msg " + " ".join(args), user)
        logs_channel = self.get_channel_id(self.settings["guild_name"], self.settings["mod_logs_channel"])
        asyncio.get_event_loop().create_task(logs_channel.send(embed=embed))

    def purge_messages(self, channel, number_of_messages, cmd, user):
        try:
            asyncio.get_event_loop().create_task(channel.purge(limit=number_of_messages))
            embed = self.create_embedded_action_logs(cmd, user)
            logs_channel = self.get_channel_id(self.settings["guild_name"], self.settings["mod_logs_channel"])
            asyncio.get_event_loop().create_task(logs_channel.send(embed=embed))
        except Exception:
            pass

    def moderate_user(self, message):
        date = datetime.now() + timedelta(hours=3)
        post_year = date.strftime("%d/%m/%Y")
        post_time = date.strftime("%H:%M:%S")
        warning_text = "{0} {1}".format(message.author.mention, random.choice(self.filters["filter_warns"]))
        sanctions_channel = self.get_channel_id(self.settings["guild_name"], self.settings["sanctions_channel"])

        moderated_text = "{0} - {1}: {2}".format(message.channel.mention, message.author.mention,
                                       message.content)
        embed = self.create_embedded_moderated_message(moderated_text, message.author, post_year, post_time)
        role = [discord.utils.find(lambda r: r.name == self.settings["banned_role"], message.guild.roles)]
        # delete the message
        asyncio.get_event_loop().create_task(message.delete())
        # warn the user
        asyncio.get_event_loop().create_task(message.channel.send(warning_text))
        # send the message to sanctions channel
        asyncio.get_event_loop().create_task(sanctions_channel.send(embed=embed))
        # change the roles to banned
        asyncio.get_event_loop().create_task(message.author.edit(roles=role))

    async def change_member_nickname(self, member, new_nick):
        await member.edit(nick=new_nick)

    async def check_for_invites(self, message):
        bot_guild = self.get_guild_id(self.settings["guild_name"])
        active_invites = await bot_guild.invites()
        texts = message.content.split()
        for text in texts:
            try:
                invite = await self.client.fetch_invite(text)
                if invite not in active_invites:
                    self.moderate_user(message)
            except Exception:
                pass

    async def give_role(self, guild, member, role_name):
        role = self.get_role_id(guild.name, role_name)
        await member.add_roles(role)

    def inform_suspicious_message(self,user, channel, message_content):
        text = "@everyone Uygunsuz mesaj şüphesi:\n\n %s - %s: %s" % (user.mention, channel.mention, message_content)
        staff_channel = self.get_channel_id(self.settings["guild_name"], self.settings["staff_channel"])

        asyncio.get_event_loop().create_task(staff_channel.send(text))

    def get_response_answer(self, message):
        k = ""
        for keyword in self.responses.keys():
            if keyword in message.content.lower():
                k = keyword
                break
        text = "{0} {1}".format(message.author.mention, random.choice(self.responses[k]))
        asyncio.get_event_loop().create_task(message.channel.send(text))

    def create_embedded_board_message(self, username, realm, board, thread_title, thread_url, post, author_url,
                                      author_icon, post_year, post_time):
        thread_url = thread_url.replace(" ","%20")
        author_icon = author_icon.replace(" ","%20")
        author_url = author_url.replace(" ","%20")
        embed = discord.Embed(title="Konu adı: {0}".format(thread_title), url=thread_url,
                              description="{0} panosunda açıldı.".format(board))
        embed.set_author(name="{} {} tarafından yeni konu açıldı!".format(username, realm),
                         url=author_url, icon_url=author_icon)
        embed.set_thumbnail(url="https://lolstatic-a.akamaihd.net/apollo/assets/vb/boards-wallpaper.jpg")
        embed.add_field(name="İçerik:", value=post, inline=False)
        embed.set_footer(text="Tarih: {0} Saat: {1}".format(post_year, post_time))
        return embed

    def create_embedded_deleted_message(self, user, message, post_year, post_time):
        embed = discord.Embed(title="💬❌ Silinen mesaj tespit edildi", description=message)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text="Tarih: {0} Saat: {1}".format(post_year, post_time))
        return embed

    def create_embedded_moderated_message(self, message, user, post_year, post_time):
        embed = discord.Embed(title="⛔ Bir ceza verildi", description=message)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text="Tarih: {0} Saat: {1}".format(post_year, post_time))
        return embed

    def create_embedded_action_logs(self, message, user):
        date = datetime.now() + timedelta(hours=3)
        post_year = date.strftime("%d/%m/%Y")
        post_time = date.strftime("%H:%M:%S")

        embed = discord.Embed(title="❗ Moderasyon komutu kullanıldı", description=message)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text="Tarih: {0} Saat: {1}".format(post_year, post_time))
        return embed

    def create_embedded_verification(self, username, key):
        embed = discord.Embed()
        embed.add_field(name="Sihirdar Adı", value=username, inline=True)
        embed.add_field(name="Harici Onaylama Kodu", value=key, inline=True)
        embed.set_image(url="https://cdn.discordapp.com/attachments/381812662088105986/622183230166269963/verification.gif")

        embed.set_footer(
            text= self.settings["guild_name"] + " verification system isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.")
        return embed

    def get_channel_id(self, guild_name, channel_name):
        return discord.utils.get(self.client.get_all_channels(), guild__name=guild_name, name=channel_name)

    def get_role_id(self, guild_name, role_name):
        guild = self.get_guild_id(guild_name)
        return discord.utils.find(lambda r: r.name == role_name, guild.roles)

    def get_guild_id(self, guild_name):
        return discord.utils.find(lambda s: s.name == guild_name, self.client.guilds)

    def get_member(self, member_id, guild):
        return discord.utils.find(lambda m: m.id == member_id, guild.members)

    def flip_coin(self, channel):
        asyncio.get_event_loop().create_task(channel.send(self.command_texts["flippingCoin"]))

        async def flipcoin():
            await asyncio.sleep(2)
            await channel.send(random.choice(["Yazı!", "Tura!"]))

        asyncio.get_event_loop().create_task(flipcoin())

    async def check_verification(self, channel, author):
        def check_verification(message):
            verified = "!onayladım"
            cancelled = "!iptal"
            return message.content in [verified, cancelled] and message.author == author

        try:
            msg = await self.client.wait_for('message', check=check_verification, timeout=5.0)
            if msg == "!iptal":
                await channel.send(self.command_texts["verificationCancelled"])
            elif msg == "!onayladım":
                return 1
        except asyncio.TimeoutError:
            await channel.send(self.command_texts["verificationTimeout"])


