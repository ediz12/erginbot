from bot.erginbot import DiscordBot
from bot.bridge import Bridge
import asyncio


class FactoryHandler(object):
    def __init__(self, is_local):
        self.loop = asyncio.get_event_loop()
        self.factory_list = {}
        self.is_local = is_local
        self.start()

    def start(self):
        bot = DiscordBot(self)
        task = self.loop.create_task(bot.begin())
        self.factory_list["discord"] = bot

        if not self.is_local:
            coro = self.loop.create_connection(lambda: Bridge(self), 'localhost', 12122)
            bridge_coro = self.loop.run_until_complete(coro)
            _, bridge = bridge_coro
            self.factory_list["bridge"] = bridge

        self.loop.run_until_complete(task)
