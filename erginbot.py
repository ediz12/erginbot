import codecs
import json
import logging
import random
import asyncio
import discord
from datetime import datetime, timedelta
import operator
from discordutils.lolboards import LoLBoardsGetter
import string

logging.basicConfig(level=logging.INFO)


class Discordbot(discord.Client):
    def __init__(self, factory=None):
        super().__init__()
        self.lol_boards = LoLBoardsGetter()
        self.ergin_data = self.load_discord_info()
        self.token = self.ergin_data["token"]

        self.raffle_mode = False
        self.userlist = []
        self.admins = ["rastai", "ediz12", "thâ jedi", "alastâir"]
        self.lol_boards_task = None


        self.factory_list = None
        self.loop = asyncio.get_event_loop()

        if factory != None:
            self.factory_list = factory.factory_list
            self.loop = factory.loop
        else:
            self.run(self.token)

    async def on_ready(self):
        logging.info("Connected as: {0}".format(self.user.name))
        self.lol_boards_task = asyncio.Task(self.check_lol_boards())
        self.loop.call_soon(self.lol_boards_task)

    async def begin(self):
        await self.start(self.token)


    async def on_message(self, message):
        channel = message.channel
        member = message.author
        msg = message.content
        server = message.server
        logging.info("[{}][{}][{}] {}".format(server, channel, member, msg))

        if member.name == self.user.name:
            return

        if msg.startswith("!"):
            commands = msg[1:].split()
            if commands[0] == "addfilter" and member.name.lower() in self.admins:
                res = self.add_filter(commands[1])
                await self.send_message(channel, self.ergin_data["addFilterResult" + str(res)].format(commands[1]))

            elif commands[0] == "removefilter" and member.name.lower() in self.admins:
                res = self.remove_filter(commands[1])
                await self.send_message(channel, self.ergin_data["removeFilterResult" + str(res)].format(commands[1]))

            elif commands[0] == "showfilter" and member.name.lower() in self.admins:
                text = ", ".join(self.ergin_data["filters"])
                await self.send_message(channel, "Ekli kelimeler: " + text)

            elif commands[0] == "lsfirstmembers" and member.name == "ediz12":
                text = "\n".join(self.list_first_members(server))
                for i in range((int(len(text) / 2000)) + 1):
                    await self.send_message(channel, text[i * 2000:(i * 2000) + 2000])

            elif commands[0] == "flipcoin":
                await self.send_message(channel, "Yazı tura atılıyor...")

                async def flipcoin():
                    await asyncio.sleep(2)
                    await self.send_message(channel, random.choice(["Yazı!", "Tura!"]))

                self.loop.create_task(flipcoin())

            elif commands[0] == "rafflemode" and member.name.lower() in self.admins:
                self.raffle_mode = not self.raffle_mode
                await self.send_message(channel, "Raffle modu durumu: %s (Komut: !kelkodver)" % self.raffle_mode)

            elif commands[0] == "kelkodver" and self.raffle_mode:
                if member.mention not in self.userlist:
                    await self.send_message(channel, "%s: çekilişe katıldınız." % member.mention)
                    self.userlist.append(member.mention)

            elif commands[0] == "listparticipants" and member.name.lower() in self.admins:
                await self.send_message(channel, ", ".join(self.userlist))

            elif commands[0] == "pickwinner" and member.name.lower() in self.admins:
                winner = random.choice(self.userlist)
                self.userlist.remove(winner)
                await self.send_message(channel, "Kazanan: %s" % winner)

            elif commands[0] == "random":
                rd = "".join([random.choice(string.ascii_lowercase) for i in range(20)])
                await self.send_message(channel, member.mention + " " + rd)

            elif commands[0] == "purge" and self.get_role_id(
                    "gergin") in member.roles:  # and discord.Object(id = self.get_role_id("gergin")) in member.roles:
                if len(commands) != 2:
                    await self.send_message(channel, "Kullanım: !purge <mesaj sayısı>")
                else:
                    msgs = await self.purge_from(channel, limit=int(commands[1]))
                    ann_channel = self.get_channel_id(server.name, "duyurular_ozel")
                    msg = ":speech_left: :x: %s - %s: %s mesaj silindi." % (member.mention, channel.mention, len(msgs))
                    await self.send_message(ann_channel, msg)

            elif commands[0] == "perms" and member.name.lower() in self.admins:
                await self.send_message(channel, channel.permissions_for(
                    server.get_member(discord.Object(id=303540634722107403))))

            elif commands[0] == "msg" and member.name.lower() in self.admins:
                chan, msg = discord.Object(id=int(commands[1])), " ".join(commands[2:])
                await self.send_message(chan, msg)

        else:
            if any(insult in msg.lower().split() for insult in
                   self.ergin_data["filters"]) or "discord.gg/" in msg.lower():
                text = "{0} {1}".format(member.mention, random.choice(self.ergin_data["filter_warns"]))

                mod_text = ":no_entry: :no_entry: {0}: {1}".format(member.mention, msg)

                await self.delete_message(message)
                if channel.name != "onay":
                    await self.send_message(channel, text)
                    await self.send_message(self.get_channel_id(server.name, "moderasyon"),
                                            mod_text)
                else:
                    await self.send_message(self.get_channel_id(server.name, "moderasyon"),
                                            mod_text)
                    await self.kick(member)

                role = discord.utils.find(lambda r: r.name == 'Cezalı', server.roles)
                await self.replace_roles(member, role)

            if any(keyword in msg.lower() for keyword in self.ergin_data["responses"].keys()):
                k = ""
                for keyword in self.ergin_data["responses"].keys():
                    if keyword in msg.lower():
                        k = keyword
                        break
                text = "{0} {1}".format(member.mention, random.choice(self.ergin_data["responses"][k]))
                await self.send_message(channel, text)

    async def on_message_delete(self, message):
        """text = "Silinen mesaj tespit edildi:\n**Kullanıcı:** {0}\n**Mesaj:** {1}\n**Kanal:** {2}".format(
            message.author.mention,
            message.content, message.channel)"""
        text = ":speech_left: :x: {0} - {1}: {2}".format(message.channel.mention, message.author.mention,
                                                         message.content)
        await self.send_message(self.get_channel_id("League of Legends Türkiye - (Topluluk Sunucusu)",
                                                    "silinen_mesajlar"),
                                text)

    def get_channel_id(self, server, channel):
        channel = discord.utils.get(self.get_all_channels(), server__name=server, name=channel)
        return channel

    def get_role_id(self, role):
        server = discord.utils.find(lambda s: s.name == 'League of Legends Türkiye - (Topluluk Sunucusu)',
                                    self.servers)
        role = discord.utils.find(lambda r: r.name == role, server.roles)
        return role

    @staticmethod
    def load_discord_info():
        with codecs.open("discordutils/ergindata.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def save_discord_info(self):
        with codecs.open("discordutils/ergindata.json", "w", encoding="utf-8") as f:
            json.dump(self.ergin_data, f, sort_keys=True, indent=2, ensure_ascii=False)

    def add_filter(self, message):
        try:
            self.ergin_data["filters"].append(message)
            self.save_discord_info()
            return True
        except Exception:
            return False

    def remove_filter(self, message):
        try:
            self.ergin_data["filters"].remove(message)
            self.save_discord_info()
            return True
        except ValueError:
            return False

    def check_lol_boards(self):
        while True:
            threads = self.lol_boards.check_new_posts()

            for thread in reversed(threads):
                post_time = datetime.strptime(thread["post_time"][:-5], "%Y-%m-%dT%H:%M:%S.%f") + timedelta(hours=3)
                year = post_time.strftime("%d/%m/%Y")
                time = post_time.strftime("%H:%M:%S")
                text = "**{0}** {1} tarafından **{2}** panosunda **{3}** adlı konu açıldı. ({4})\n\n**İçerik:**\n{5}" \
                       "\n\n*Tarih: {6} Saat: {7}*\n{8}".format(thread["username"], thread["realm"], thread["board"],
                                                                thread["thread_title"], thread["thread_url"],
                                                                thread["post"], year, time, "\\_" * 93)

                self.loop.create_task(self.send_message(self.get_channel_id(
                    "League of Legends Türkiye - (Topluluk Sunucusu)", "panolar"), text))
            yield from asyncio.sleep(15)

    def list_first_members(self, server):
        memberstime = {}
        for member in server.members:
            if member.nick:
                memberstime[member.nick] = member.joined_at
            else:
                memberstime[member.name] = member.joined_at
        members = sorted(memberstime.items(), key=operator.itemgetter(1))
        lst_members = ["%s - %s" % (name, time.strftime("%d/%m/%Y - %H:%M:%S")) for name, time in members]
        for i, member in enumerate(lst_members):
            lst_members[i] = "%s. %s" % (i + 1, lst_members[i])
        return lst_members


class Bridge(asyncio.Protocol):
    def __init__(self, factory):
        self.sep = chr(12)
        self.conn = None
        self.factory_list = factory.factory_list
        self.loop = factory.loop

    def connection_made(self, transport):
        self.conn = transport
        print("Connected")
        self.authenticate()

    def connection_lost(self, exc):
        pass

    def data_received(self, data):
        data = data.decode().split(self.sep)[1:-1]
        while len(data) > 0:
            req = data[0]

            if req == "auth_success":
                data = data[2:]

            if req == "discord_lol_auth":
                who = data[1]
                data = data[2:]
                who = who.split("|")
                self.change_nick(who[0], who[1])
                self.grant_role(who[0])

    def send(self, *data):
        data = self.sep + ("%s" % self.sep).join(data) + self.sep
        self.conn.write(bytes(data.encode()))

    def authenticate(self):
        self.send("auth", "erginbot")

    # Discord functions below #
    def change_nick(self, member_id, nickname):
        server = discord.utils.find(lambda s: s.name == 'League of Legends Türkiye - (Topluluk Sunucusu)',
                                    self.factory_list["discord"].servers)
        member = discord.utils.find(lambda m: m.id == member_id, server.members)
        self.loop.create_task(self.factory_list["discord"].change_nickname(
            member, nickname))

    def grant_role(self, member_id):
        server = discord.utils.find(lambda s: s.name == 'League of Legends Türkiye - (Topluluk Sunucusu)',
                                    self.factory_list["discord"].servers)

        role = discord.utils.find(lambda r: r.name == 'Sihirdar', server.roles)
        member = discord.utils.find(lambda m: m.id == member_id, server.members)
        self.loop.create_task(self.factory_list["discord"].add_roles(member, role))


"""class FactoryHandler(object):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.factory_list = {}
        self.start()

    def start(self):
        bot = Discordbot(self)
        task = self.loop.create_task(bot.begin())
        self.factory_list["discord"] = bot
        coro = self.loop.create_connection(lambda: Bridge(self), 'localhost', 12122)
        bridge_coro = self.loop.run_until_complete(coro)
        _, bridge = bridge_coro
        self.factory_list["bridge"] = bridge

        self.loop.run_until_complete(task)


FactoryHandler()"""

Discordbot().run()