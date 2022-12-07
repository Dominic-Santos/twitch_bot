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
CATCH_SPECIAL_BALLS = {
    "Water": "netball",
    "Bug": "netball",
    "Dark": "nightball",
    "Ghost": "phantomball",
    "Poison": "cipherball",
    "Psychic": "cipherball",
    "Ice": "frozenball"
}

SETTINGS_FILE = "pokemon.json"
POKEDEX_FILE = "pokedex.json"

BALANCE_TRIGGER = 1
ITEM_MIN_AMOUNT = 30
ITEM_MIN_PURCHASE = 10
ITEM_PRIORITY = ["pokeball", "ultraball"]
ITEM_PRICES = {
    "pokeball": 300,
    "greatball": 600,
    "ultraball": 1000,
}


class Pokedex(object):
    def __init__(self):
        self.types = {}
        self.load()

    def get(self, pokemon):
        return self.types.get(pokemon, [])

    def get_data(self, pokemon):
        res = requests.get(POKEMON_INFO_URL.format(pokemon=pokemon), headers=HEADERS)
        soup = BeautifulSoup(res.content, "html.parser")
        return soup

    def get_type_request(self, pokemon):
        try:
            data = self.get_data(pokemon)
            typedata = data.find("div", class_="dtm-type").find_all("a")
            types = [t.text for t in typedata]
            self.types[pokemon] = types
            self.save()
        except:
            pass

    def get_type(self, pokemon):
        if pokemon in self.types:
            return self.types[pokemon]

        self.get_type_request(pokemon)

        return self.get(pokemon)

    def save(self):
        with open(POKEDEX_FILE, "w") as f:
            f.write(json.dumps(self.types, indent=4))

    def load(self):
        try:
            with open(POKEDEX_FILE, "r") as f:
                self.types = json.load(f)
        except:
            self.types = {}

    @staticmethod
    def clean_name(pokemon):
        end = pokemon
        if pokemon.startswith("Nidoran"):
            end = "Nidoran-{sex}".format(sex="male" if pokemon.endswith("♂") else "female")
        elif pokemon == "Mime":
            end = "Mime-jr"
        elif pokemon.startswith("Mr"):
            end = "Mr-{poke}".format(poke=pokemon.split(" ")[1])
        end = end.replace("’", "")
        return end


class Inventory(object):
    def __init__(self):
        self.reset()
        self.last_used = None

    def __str__(self):
        return "Balance: $" + str(self.cash) + " " + ", ".join(["{item}: {amount}".format(item=item, amount=self.get_item(item)) for item in sorted(self.items.keys())])

    def get(self):
        return self.items

    def set(self, items):
        self.items = items

    def reset(self):
        self.items = {}
        self.cash = 0

    def add_item(self, item, amount):
        self.items[item] = self.get_item(item) + amount

    def remove_item(self, item, amount):
        self.items[item] = self.get_item(item) - amount

    def get_item(self, item):
        return self.items.get(item, 0)

    def set_item(self, item, amount):
        self.items[item] = amount

    def have_item(self, item):
        return self.get_item(item) > 0

    def use(self, item):
        if self.have_item(item):
            self.remove_item(item, 1)
            self.last_used = item

    def set_cash(self, cash):
        self.cash = cash

    def get_catch_ball(self, types=[], repeat=False):
        if repeat:
            if self.have_item("repeatball"):
                return "repeatball"

        if types is not None:
            for t in sorted(types):
                if t in CATCH_SPECIAL_BALLS:
                    if self.have_item(CATCH_SPECIAL_BALLS[t]):
                        return CATCH_SPECIAL_BALLS[t]

        for item in CATCH_BALL_PRIORITY:
            if self.have_item(item):
                return item

        return None


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
        self.last_have = None

        self.rechecking = False

        self.settings = {}
        self.pending_purchases = []

        self.inventory = Inventory()
        self.pokedex = Pokedex()

        self.load_settings()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            f.write(json.dumps({
                "inventory": self.inventory.get(),
                "settings": self.settings
            }, indent=4))

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                j = json.load(f)
                self.inventory.set(j.get("inventory", {}))
                self.settings = j.get("settings", {})
        except:
            self.settings = {}

    def set_cash(self, cash):

        if cash < self.inventory.cash and len(self.pending_purchases) > 0:
            for item, amount in self.pending_purchases:
                self.inventory.add_item(item, amount)
                if item in ITEM_PRIORITY and amount > 9:
                    self.inventory.add_item("premierball", amount // 10)
            self.pending_purchases = []

        self.inventory.set_cash(cash)

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

    def last_attempt(self, set_to=None, channel=None, have=None):
        if set_to is None:
            return self.last_catch, self.last_channel, self.last_have

        self.last_catch = set_to
        self.last_channel = channel
        self.last_have = have
        self.rechecking = False

    def set_rechecking(self, rechecking):
        self.rechecking = rechecking

    def get_catch_message(self, use=True, repeat=False):
        selected = self.inventory.get_catch_ball(self.last_type, repeat)

        if selected is not None:
            if use:
                self.inventory.use(selected)
            return f"!pokecatch {selected}"

        return "!pokecatch"

    def check_balance_tick(self):
        self.check_balance_counter += 1

        if self.check_balance_counter == BALANCE_TRIGGER:
            self.check_balance_counter = 0
            return True

        return False

    def check_balance(self):
        if not self.need_items():
            return False
        return self.check_balance_tick()

    def need_items(self):
        for item in ITEM_PRIORITY:
            if self.inventory.get_item(item) < ITEM_MIN_AMOUNT:
                return True
        return False

    def get_purchase_list(self, buy=False):
        cash = self.inventory.cash + 0
        purchases = []

        for item in ITEM_PRIORITY:
            have = self.inventory.get_item(item)
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
        return str(self.inventory)

    def get_pokemon_type(self, pokemon):
        self.last_type = self.pokedex.get_type(pokemon)
        return self.last_type

    def get_type_mission(self):
        m = self.settings.get("type_mission", None)
        t = self.settings.get("type_target", None)
        c = self.settings.get("type_caught", 0)
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
