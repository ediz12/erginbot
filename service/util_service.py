import random
import string

class UtilService(object):

    def create_random_laugh(self):
        return "".join([random.choice(string.ascii_lowercase) for i in range(20)])