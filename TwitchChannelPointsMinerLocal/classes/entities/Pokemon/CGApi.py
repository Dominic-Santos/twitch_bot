import requests

BASE_URL = "https://poketwitch.bframework.de/api/game/ext/"
TRAINER_URL = f"{BASE_URL}trainer/"

ERROR_JWT_EXPIRE = -24


class API(object):
    def __init__(self, auth_token=None):
        self.auth = auth_token

    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv/",
            "Origin": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv",
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.auth
        }

    def get_auth_token(self):
        # placeholder to be replaced
        pass

    def refresh_auth(self):
        self.auth = self.get_auth_token()

    def _get_data(self, method, url, payload):
        if self.auth is None:
            return None

        response = requests.request(method, url, headers=self.get_headers(), json=payload)
        return response.json()

    def _do_request(self, method, url, payload={}):
        data = self._get_data(method, url, payload)

        if data is None or data.get("error", 0) == ERROR_JWT_EXPIRE:
            # jwt expired refresh token
            self.refresh_auth()

            # get data again, basically a retry
            data = self._get_data(method, url, payload)

        return data

    def get_pokemon(self, pokemon_id):
        return self._do_request("GET", TRAINER_URL + f"pokemon/{pokemon_id}/")

    def get_all_pokemon(self):
        return self._do_request("GET", TRAINER_URL + "pokemon/")

    def set_name(self, pokemon_id, name):
        return self._do_request("POST", TRAINER_URL + f"change-nickname/{pokemon_id}/", payload={"nickname": name})

    def get_inventory(self):
        return self._do_request("GET", TRAINER_URL + f"inventory/")

    def get_pokedex(self):
        return self._do_request("GET", TRAINER_URL + f"pokedex/")

    def wondertrade(self, pokemon_id):
        # response is {"pokemon": {the info}}
        return self._do_request("POST", TRAINER_URL + f"wonder-trade/{pokemon_id}/")
