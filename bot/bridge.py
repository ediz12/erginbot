import asyncio
import discord

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
        guild = discord.utils.find(lambda s: s.name == 'League of Legends Türkiye - (Topluluk Sunucusu)',
                                    self.factory_list["discord"].guilds)
        member = discord.utils.find(lambda m: m.id == member_id, guild.members)
        self.loop.create_task(member.edit(nickname))

    def grant_role(self, member_id):
        guild = discord.utils.find(lambda s: s.name == 'League of Legends Türkiye - (Topluluk Sunucusu)',
                                    self.factory_list["discord"].guilds)

        role = discord.utils.find(lambda r: r.name == 'Sihirdar', guild.roles)
        member = discord.utils.find(lambda m: m.id == member_id, guild.members)
        self.loop.create_task(self.factory_list["discord"].add_roles(member, role))
