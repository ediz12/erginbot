import string
import random
import asyncio
from service.file_service import FileService
from service.discord_service import DiscordService

import cassiopeia as cass
from cassiopeia import Summoner
from cassiopeia.datastores.riotapi.common import APIRequestError


class VerificationService(object):
    def __init__(self, client):
        self.characters = string.ascii_uppercase + string.digits

        self.file_service = FileService()
        self.discord_service = DiscordService(client)
        self.client = client

        self.command_texts = self.file_service.load_json_file("resources/command_texts.json")
        self.settings = self.file_service.load_json_file("resources/settings.json")
        self.verify_pending = []

        cass.set_riot_api_key(self.settings["riot_api_key"])
        cass.set_default_region("TR")

    def random_generator(self):
        return "".join(random.choice(self.characters) for _ in range(5))

    def generate_code(self):
        return "-".join([self.random_generator() for _ in range(5)])

    async def check_verification(self, channel, author, summoner_name, expected_verification):
        try:
            summoner = Summoner(name=summoner_name)
            verification_string = summoner.verification_string
            summoner_name = summoner.name
            if (expected_verification == verification_string):
                await channel.send(self.command_texts["correctVerification"])
                await self.discord_service.change_member_nickname(author, summoner_name)
                await self.discord_service.give_role(channel.guild, author, self.settings["verified_role"])
                self.verify_pending.remove(author)
            else:
                wrong_text = self.command_texts["wrongVerification"].format(verification_string, expected_verification)
                await channel.send(wrong_text)
                self.verify_pending.remove(author)
                await self.wait_and_verify(channel, author, summoner_name, expected_verification)

        except APIRequestError as e:
            await channel.send(str(e))
            self.verify_pending.remove(author)
        except Exception as e:
            await channel.send(self.command_texts["noVerification"].format(summoner_name) + " Sunucu ekibine iletmek için aldığınız hata: " + str(e))
            self.verify_pending.remove(author)
            await self.wait_and_verify(channel, author, summoner_name, expected_verification)


    async def wait_and_verify(self, channel, author, summoner_name, expected_verification=None):
        if author in self.verify_pending:
            await channel.send(self.command_texts["verificationAlreadyPending"])
            return

        self.verify_pending.append(author)

        if expected_verification is None:
            expected_verification = self.generate_code()
            verification_message = self.discord_service.create_embedded_verification(summoner_name, expected_verification)
            verification_help = "\n\n".join([self.command_texts["verificationSteps"], self.command_texts["verificationPossibleError"]])
            await channel.send(verification_help, embed=verification_message)

        def check(message):
            verified = "!onayladım"
            cancelled = "!iptal"
            return message.content in [verified, cancelled] and message.author == author

        try:
            msg = await self.client.wait_for('message', check=check, timeout=300.0)
            if msg.content == "!iptal":
                await channel.send(self.command_texts["verificationCancelled"])
                self.verify_pending.remove(author)
            elif msg.content == "!onayladım":
                await self.check_verification(channel, author, summoner_name, expected_verification)
        except asyncio.TimeoutError:
            await channel.send(self.command_texts["verificationTimeout"].format(summoner_name))
            self.verify_pending.remove(author)
