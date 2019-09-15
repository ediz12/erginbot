import asyncio
import logging
import random
import time
from datetime import datetime, timedelta

import discord

from service.file_service import FileService
from service.discord_service import DiscordService
from bot.command_handler import CommandHandler
from utils.lolboards import LoLBoardsGetter

log = logging.getLogger()
log.setLevel(logging.INFO)

logger_file = open("logs/ergin-bot %s.txt" % time.strftime("%Y-%m-%d %H-%M-%S"), 'a', encoding="utf-8")
logging.basicConfig(stream=logger_file,
                    level=logging.INFO,
                    format=u"%(message)s")

stream_handler = logging.StreamHandler()
log.addHandler(stream_handler)


class DiscordBot(discord.Client):
    def __init__(self, factory):
        super().__init__()
        self.factory = factory
        self.loop = asyncio.get_event_loop()

        self.file_service = FileService()
        self.discord_service = DiscordService(self)

        self.settings = self.file_service.load_json_file("resources/settings.json")
        self.lol_data = self.file_service.load_json_file("resources/lol_data.json")
        self.command_texts = self.file_service.load_json_file("resources/command_texts.json")
        self.lol_boards = LoLBoardsGetter()
        self.command_handler = CommandHandler(self)

        self.raffle_mode = False
        self.tasks = {}

    async def begin(self):
        await self.start(self.settings["token"])

    async def on_ready(self):
        logging.info("Connected as: {0}".format(self.user.name))
        self.tasks["lol boards task"] = asyncio.Task(self.check_lol_boards())

    async def on_member_join(self, member):
        nick = self.command_texts["newUsernameNickname"].format(random.choice(self.lol_data["champions"]))
        welcome_message = self.command_texts["welcomeMessage"].format(member.mention)
        channel = self.discord_service.get_channel_id(self.settings["guild_name"], self.settings["welcome_channel"])

        await channel.send(welcome_message)
        await member.edit(nick=nick)

    async def on_message_delete(self, message):
        message_time = message.created_at + timedelta(hours=3)
        pyear = message_time.strftime("%d/%m/%Y")
        ptime = message_time.strftime("%H:%M:%S")
        text = "{0} - {1}: {2}".format(message.channel.mention, message.author.mention,
                                       message.content)
        embed = self.discord_service.create_embedded_deleted_message(message.author, text, pyear, ptime)

        channel = self.discord_service.get_channel_id(self.settings["guild_name"],
                                                      self.settings["deleted_messages_channel"])

        await channel.send( embed=embed)

    async def on_message(self, message):
        channel = message.channel
        author = message.author
        message_content = message.content
        guild = message.guild
        logging.info("[{0}][{1}][{2}] {3}".format(guild, channel, author, message_content))

        if author.name == self.user.name:
            return
        else:
            result = await self.command_handler.handle(message, self)

            if result:
                for i in range((int(len(result) / 2000)) + 1):
                    # If we get a response longer than 2000 characters, split it into different messages
                    await channel.send(result[i * 2000:(i * 2000) + 2000])

    def check_lol_boards(self):
        while True:
            threads = self.lol_boards.check_new_posts()

            for thread in reversed(threads):
                post_time = datetime.strptime(thread["post_time"][:-5], "%Y-%m-%dT%H:%M:%S.%f") + timedelta(hours=3)
                pyear = post_time.strftime("%d/%m/%Y")
                ptime = post_time.strftime("%H:%M:%S")

                embed = self.discord_service.create_embedded_board_message(thread["username"], thread["realm"],
                                                                           thread["board"], thread["thread_title"],
                                                                           thread["thread_url"], thread["post"],
                                                                           thread["author_url"], thread["author_icon"],
                                                                           pyear, ptime)

                if thread["board"] == "Duyurular":
                    channel = self.discord_service.get_channel_id(self.settings["guild_name"],
                                                                  self.settings["board_announcements_channel"])
                    announcement_role = self.discord_service.get_role_id(self.settings["guild_name"],
                                                                         self.settings["board_announcements_role"])
                    self.loop.create_task(channel.send(announcement_role.mention, embed=embed))
                else:
                    channel = self.discord_service.get_channel_id(self.settings["guild_name"],
                                                                  self.settings["board_channel"])
                    self.loop.create_task(channel.send(embed=embed))

            yield from asyncio.sleep(15)
