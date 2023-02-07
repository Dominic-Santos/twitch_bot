import requests


class DiscordAPI(object):
    def __init__(self, auth_token=None):
        self.auth_token = auth_token

    def get_headers(self):
        return {"Authorization": self.auth_token}

    def post(self, url, content):
        if self.auth_token is not None:
            requests.post(url, headers=self.get_headers(), data={"content": content})

    def get(self, url):
        if self.auth_token is not None:
            r = requests.get(url, headers=self.get_headers())
            data = r.json()
            return data
