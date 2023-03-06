import requests

BASE_URL = "https://poketwitch.bframework.de/api/game/ext/"
TRAINER_URL = f"{BASE_URL}trainer/"
SHOP_URL = f"{BASE_URL}shop/"


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
        return self._do_request("GET", TRAINER_URL + "inventory/")

    def get_pokedex(self):
        return self._do_request("GET", TRAINER_URL + "pokedex/")

    def get_pokedex_info(self, pokedex_id):
        # response {"content": {"pokedex_id": 1, "name": "Bulbasaur", "description": "etc", "weight": 6.9, "generation": 1, "type1": "poison", "type2": "grass", "base_stats": {"hp": 45, "speed": 45, "attack": 49, "defense": 49, "special_attack": 65, "special_defense": 65}}}
        return self._do_request("GET", TRAINER_URL + f"pokedex/info/?pokedex_id={pokedex_id}")

    def wondertrade(self, pokemon_id):
        # response is {"pokemon": {the info}}
        return self._do_request("POST", TRAINER_URL + f"wonder-trade/{pokemon_id}/")

    def get_missions(self):
        return self._do_request("GET", TRAINER_URL + "mission/")

    def get_shop(self):
        """
        returns:
        {
            "shopItems": [
                {
                    "name": "ultra_ball",
                    "price": 1000,
                    "displayName": "Ultra Ball",
                    "description": "An ultra-high-performance Pok\u00e9 Ball that provides a higher success rate for catching Pok\u00e9mon than a Great Ball.",
                    "type": 2,
                    "catchRate": "80%",
                    "category": "ball",
                    "tmType": null
                }, ...
            ]
        }

        """
        return self._do_request("GET", SHOP_URL)

    def buy_item(self, item_name, amount):
        # returns {"cash": 123}
        return self._do_request("POST", SHOP_URL + "purchase/", payload={"item_name": item_name, "amount": amount})
