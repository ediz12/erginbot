import requests

class AccessDiscord(object):
    def __init__(self, code):
        self.code = code
        self.api = "https://discordapp.com/api/v6"

    def exchange_code(self):
        data = {
            'client_id': "303540634722107403",
            'client_secret': "bGhzyEFj_o2Joz2olDEmJfHisP6854Ii",
            'grant_type': "authorization_code",
            'code': self.code,
            'redirect_uri': "http://www.riddlematic.com/confirmed"
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post('%s/oauth2/token' % self.api, params=data, headers=headers)
        return r.json()

    def get_connections(self):
        auth_data = self.exchange_code()
        if "error" in auth_data:
            return "error"
        headers = {
            "Authorization": "{0} {1}".format(auth_data["token_type"], auth_data["access_token"]),
            "User-Agent": "Test"
        }
        r = requests.get(self.api + "/users/@me/connections", headers=headers)
        ur = requests.get(self.api + "/users/@me", headers=headers)
        return (r.json(), ur.json())