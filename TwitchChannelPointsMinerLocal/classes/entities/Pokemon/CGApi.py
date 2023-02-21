import requests

URL = "https://poketwitch.bframework.de/api/game/ext/trainer/"


class API(object):
    def __init__(self, auth_token):
        self.auth = auth_token

    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv/",
            "Origin": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv",
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.auth
        }

    def _do_request(self, method, url, payload={}):
        response = requests.request(method, url, headers=self.get_headers(), json=payload)
        return response.json()

    def get_pokemon(self, pokemon_id):
        return self._do_request("GET", URL + f"pokemon/{pokemon_id}/")

    def get_all_pokemon(self):
        return self._do_request("GET", URL + "pokemon/")

    def set_name(self, pokemon_id, name):
        return self._do_request("POST", URL + f"change-nickname/{pokemon_id}/", payload={"nickname": name})
