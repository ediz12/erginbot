import random

class RaffleService(object):
    def __init__(self):
        self.raffle_mode = False
        self.raffle_mode_participants = []

    def toggle_raffle_mode(self):
        self.raffle_mode = not self.raffle_mode
        return self.raffle_mode

    def add_participant(self, mentionable_author):
        if mentionable_author not in self.raffle_mode_participants:
            self.raffle_mode_participants.append(mentionable_author)
            return mentionable_author
        else:
            return None

    def list_participants(self):
        return self.raffle_mode_participants

    def pick_winner(self):
        if len(self.raffle_mode_participants) == 0:
            return None
        winner = random.choice(self.raffle_mode_participants)
        self.raffle_mode_participants.remove(winner)
        return winner
