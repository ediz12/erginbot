from service.file_service import FileService
from service.filter_service import FilterService
from service.discord_service import DiscordService
from service.raffle_service import RaffleService
from service.util_service import UtilService
from service.verification_service import VerificationService

import asyncio

class CommandHandler(object):
    def __init__(self, client):
        self.client = client
        self.guild = None
        self.channel = None
        self.author = None
        self.message_content = None
        self.staff_role = None

        self.loop = asyncio.get_event_loop()
        self.filter_service = FilterService()
        self.file_service = FileService()
        self.discord_service = DiscordService(self.client)
        self.raffle_service = RaffleService()
        self.util_service = UtilService()
        self.verification_service = VerificationService(client)

        self.settings = self.file_service.load_json_file("resources/settings.json")
        self.filters = self.file_service.load_json_file("resources/filters.json")
        self.responses = self.file_service.load_json_file("resources/responses.json")
        self.command_texts = self.file_service.load_json_file("resources/command_texts.json")

    async def handle(self, message, client):
        self.guild = message.guild
        self.channel = message.channel
        self.author = message.author
        self.message_content = message.content
        self.client = client
        self.staff_role = self.discord_service.get_role_id(self.settings["guild_name"], self.settings["staff_role"])
        self.banned_role = self.discord_service.get_role_id(self.settings["guild_name"], self.settings["banned_role"])
        self.verified_role = self.discord_service.get_role_id(self.settings["guild_name"], self.settings["verified_role"])

        if (self.guild is not None) and self.banned_role in self.author.roles:
            return

        if self.message_content.startswith(self.settings["prefix"]):
            commands = self.message_content[1:].split()
            command = "_cmd_{0}".format(commands[0].lower())
            if hasattr(self, command):
                return getattr(self, command)(commands[1:])
        else:
            if any(word in self.filters["filters"] for word in self.message_content.lower().split()):
                self.discord_service.moderate_user(message)
            elif any(word in self.filters["suspicious"] for word in self.message_content.lower().split()):
                self.discord_service.inform_suspicious_message(self.author, self.channel, self.message_content)
            elif "discord.gg" in self.message_content:
                await self.discord_service.check_for_invites(message)
            elif any(keyword in self.message_content.lower() for keyword in self.responses.keys()):
                self.discord_service.get_response_answer(message)
            return None

    def _cmd_addfilter(self, args):
        if len(args) == 1 and self.staff_role in self.author.roles:
            keyword = args[0]
            result = self.filter_service.add_filter(keyword)
            if result:
                self.filters["filters"].append(keyword)
            return self.command_texts["addFilterResult" + str(result)].format(keyword)
        else:
            return self.get_wrong_command_usage("badAddFilterCommand")

    def _cmd_removefilter(self, args):
        if len(args) == 1 and self.staff_role in self.author.roles:
            keyword = args[0]
            result = self.filter_service.remove_filter(keyword)
            if result:
                self.filters["filters"].remove(keyword)
            return self.command_texts["removeFilterResult" + str(result)].format(keyword)
        else:
            return self.get_wrong_command_usage("badRemoveFilterCommand")

    def _cmd_showfilter(self, args):
        if len(self.filter_service.filters["filters"]) > 0 and self.staff_role in self.author.roles:
            return ", ".join(self.filter_service.filters["filters"])
        else:
            return self.command_texts["emptyFilter"]

    def _cmd_lsfirstmembers(self, args):
        if self.staff_role in self.author.roles:
            return "\n".join(self.discord_service.list_first_members(self.guild))

    def _cmd_flipcoin(self, args):
        if self.verified_role in self.author.roles:
            self.discord_service.flip_coin(self.channel)
            return None

    def _cmd_rafflemode(self, args):
        if self.staff_role in self.author.roles:
            return self.command_texts["raffleMode" + str(self.raffle_service.toggle_raffle_mode())]

    def _cmd_kelkodver(self, args):
        if self.verified_role in self.author.roles:
            result = self.raffle_service.add_participant(self.author.mention)
            if result:
                return self.command_texts["addedNewRaffleParticipant"].format(self.author.mention)
            else:
                return self.command_texts["participantAlreadyAdded"].format(self.author.mention)

    def _cmd_lsparticipants(self, args):
        if self.staff_role in self.author.roles:
            result = self.raffle_service.list_participants()
            if len(result) == 0:
                return self.command_texts["noParticipants"]
            return ", ".join(self.raffle_service.list_participants())

    def _cmd_pickwinner(self, args):
        if self.staff_role in self.author.roles:
            result = self.raffle_service.pick_winner()
            if result:
                return self.command_texts["raffleWinner"].format(result)
            else:
                return self.command_texts["noWinners"]

    def _cmd_random(self, args):
        if self.verified_role in self.author.roles:
            return self.util_service.create_random_laugh()

    def _cmd_purge(self, args):
        if self.staff_role in self.author.roles:
            if len(args) == 1 and args[0].isnumeric():
                no_of_msgs_to_delete = int(args[0])
                self.discord_service.purge_messages(self.channel, no_of_msgs_to_delete, self.message_content, self.author)
                return None
            else:
                return self.get_wrong_command_usage("badPurgeCommand")

    def _cmd_msg(self, args):
        if len(args[0]) > 1 and self.staff_role in self.author.roles:
            self.discord_service.create_bot_message(args, self.author)
            return None
        else:
            return self.get_wrong_command_usage("badMsgCommand")

    def _cmd_riotduyuru(self, args):
        if self.verified_role in self.author.roles:
            asyncio.get_event_loop().create_task(self.discord_service.give_role(self.guild, self.author, self.settings["board_announcements_role"]))
            return self.command_texts["addedAnnouncementsRole"].format(self.settings["board_announcements_channel"])

    def _cmd_destek(self, args):
        return "https://support.riotgames.com/hc/tr"

    def _cmd_doan(self, args):
        if self.verified_role in self.author.roles:
            return "gel vs, tüm güçle alırım seni! item al gel full para dimi gel!  - doğan, 2019 https://www.youtube.com/watch?v=eoUn5toyZvY"

    def _cmd_onayyardim(self, args):
        if self.staff_role in self.author.roles:
            return "\n\n".join([self.command_texts["verificationSteps"], self.command_texts["verificationPossibleError"]])

    def _cmd_verify(self, args):
        if len(args) == 0:
            return self.get_wrong_command_usage("badVerificationCommand")

        summoner_name = " ".join(args)
        self.loop.create_task(self.verification_service.wait_and_verify(self.guild, self.author, summoner_name))

    def get_wrong_command_usage(self, which):
        return self.command_texts["correctUsage"] + self.command_texts[which]
