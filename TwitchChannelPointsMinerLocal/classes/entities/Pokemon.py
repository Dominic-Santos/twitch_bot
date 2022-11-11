import random
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

POKEMON_INFO_URL = "https://www.pokemon.com/us/pokedex/{pokemon}"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

CATCH_TRIGGER = 2
CATCH_DELAY = 90  # seconds
CATCH_BALL_PRIORITY = ["ultraball", "greatball", "premierball", "pokeball"]

SETTINGS_FILE = "pokemon.json"

BALANCE_TRIGGER = 1
ITEM_MIN_AMOUNT = 30
ITEM_MIN_PURCHASE = 10
ITEM_PRIORITY = ["pokeball", "ultraball"]
ITEM_PRICES = {
    "pokeball": 300,
    "greatball": 600,
    "ultraball": 1000,
}


class PokemonComunityGame(object):
    def __init__(self):
        self.connected = False
        self.twitch = None
        self.channel_list = []
        self.last_random = ""

        self.catch_counter = 0
        self.catch_timer = datetime.now()

        self.check_balance_counter = 0

        self.last_catch = None
        self.last_channel = None
        self.last_type = None

        self.settings = {}
        self.inventory = {}
        self.cash = 0
        self.pending_purchases = []

        self.load_settings()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            f.write(json.dumps({
                "inventory": self.inventory,
                "settings": self.settings
            }, indent=4))

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                j = json.load(f)
                self.inventory = {} if "inventory" not in j else j["inventory"]
                self.settings = {} if "settings" not in j else j["settings"]
        except:
            self.inventory = {}
            self.settings = {}

    def set_cash(self, cash):

        if cash < self.cash and len(self.pending_purchases) > 0:
            for item, amount in self.pending_purchases:
                self.add_item(item, amount)
                if item in ITEM_PRIORITY and amount > 9:
                    self.add_item("premierball", amount // 10)
            self.pending_purchases = []

        self.cash = cash

    def add_channel(self, channel):
        if channel not in self.channel_list:
            self.channel_list.append(channel)

    def remove_channel(self, channel):
        if channel in self.channel_list:
            self.channel_list.remove(channel)

    def random_channel(self):
        nr_channels = len(self.channel_list)

        if nr_channels == 0:
            return None

        if nr_channels == 1:
            self.last_random = self.channel_list[0]
        else:
            self.last_random = random.choice([channel for channel in self.channel_list if channel != self.last_random])
        return self.last_random

    def check_catch(self):
        now = datetime.now()
        if (now - self.catch_timer).total_seconds() > CATCH_DELAY:
            self.catch_timer = now
            self.catch_counter = 0

        self.catch_counter += 1

        if self.catch_counter == CATCH_TRIGGER:
            return True

        return False

    def last_attempt(self, set_to=None, channel=None):
        if set_to is None:
            return self.last_catch, self.last_channel

        self.last_catch = set_to
        self.last_channel = channel

    def add_item(self, item, amount):
        if item in self.inventory:
            self.inventory[item] = self.inventory[item] + amount
        else:
            self.inventory[item] = amount

    def get_item(self, item):
        if item in self.inventory:
            return self.inventory[item]
        return 0

    def get_catch_message(self, use=True):
        for item in CATCH_BALL_PRIORITY:
            have = self.get_item(item)
            if have > 0:
                if use:
                    self.inventory[item] = self.inventory[item] - 1
                return f"!pokecatch {item}"
        return "!pokecatch"

    def check_balance(self):
        self.check_balance_counter += 1

        if self.check_balance_counter == BALANCE_TRIGGER:
            self.check_balance_counter = 0
            return True

        return False

    def get_purchase_list(self, buy=False):
        cash = self.cash + 0
        purchases = []

        for item in ITEM_PRIORITY:
            have = self.get_item(item)
            if have < ITEM_MIN_AMOUNT:
                price = ITEM_PRICES[item] * ITEM_MIN_PURCHASE
                if price > cash:
                    break

                purchases.append((item, ITEM_MIN_PURCHASE))
                cash = cash - price
                break

        if buy:
            self.pending_purchases = purchases

        return purchases

    def get_inventory(self):
        return "Balance: $" + str(self.cash) + " " + ", ".join(["{item}: {amount}".format(item=item, amount=self.inventory[item]) for item in sorted(self.inventory.keys())])

    def get_pokemon_type(self, pokemon):
        res = requests.get(POKEMON_INFO_URL.format(pokemon=pokemon), headers=HEADERS)
        soup = BeautifulSoup(res.content, "html.parser")

        try:
            typedata = soup.find("div", class_="dtm-type").find_all("a")
            types = [t.text for t in typedata]
        except:
            types = []

        self.last_type = types
        return types

    def get_type_mission(self):
        m = None if "type_mission" not in self.settings else self.settings["type_mission"]
        t = None if "type_target" not in self.settings else self.settings["type_target"]
        c = 0 if "type_caught" not in self.settings else self.settings["type_caught"]
        return m, t, c

    def check_type_mission(self, inc=False):
        mission, target, caught = self.get_type_mission()
        is_type = False

        if mission in self.last_type:
            if target is None:
                is_type = True
            elif caught < target:
                is_type = True

        if is_type and inc:
            self.settings["type_caught"] = caught + 1

        return is_type
