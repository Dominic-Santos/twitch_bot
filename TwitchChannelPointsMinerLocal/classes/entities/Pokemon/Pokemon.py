import random
from datetime import datetime
import json

from .Discord import Discord
from .Missions import Missions
from .Inventory import Inventory
from .Pokedex import Pokedex

CATCH_TRIGGER = 10
CATCH_DELAY = 60  # seconds

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
        self.last_have = None
        self.last_alternate = ("0", "NA")

        self.rechecking = False

        self.settings = {
            "catch_everything": False,
            "catch_alternates": False,
            "catch": [],
            "catch_tiers": []
        }
        self.pending_purchases = []

        self.discord = Discord()
        self.inventory = Inventory()
        self.pokedex = Pokedex()
        self.missions = Missions()

        self.pokedex.set_discord(self.discord)
        self.missions.set_pokedex(self.pokedex)

        self.load_settings()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            to_write = {
                "inventory": self.inventory.get(),
                "settings": self.settings,
                "alternates": self.pokedex.alts,
                "missions": self.missions.data,
                "discord": self.discord.data
            }
            f.write(json.dumps(to_write, indent=4))

    def load_settings(self):
        with open(SETTINGS_FILE, "r") as f:
            j = json.load(f)
            self.set(j.get("settings", {}))
            self.inventory.set(j.get("inventory", {}))
            self.discord.set(j.get("discord", {}))
            self.pokedex.alts = j.get("alternates", [])
            self.missions.set(j.get("missions", {}))

    def set(self, settings):
        for k in settings:
            if k in self.settings:
                self.settings[k] = settings[k]

    def catch_everything(self):
        return self.settings.get("catch_everything")

    def catch_alternates(self):
        return self.settings.get("catch_alternates")

    def always_catch(self):
        return self.settings.get("catch")

    def always_catch_tiers(self):
        return self.settings.get("catch_tiers")

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

    def last_attempt(self, set_to=None, channel=None, have=None, alternate=("0", "NA")):
        if set_to is None:
            return self.last_catch, self.last_channel, self.last_have, self.last_alternate

        self.last_catch = set_to
        self.last_channel = channel
        self.last_have = have
        self.last_alternate = alternate
        self.rechecking = False

    def set_rechecking(self, rechecking):
        self.rechecking = rechecking

    def get_catch_message(self, use=True, repeat=False, best=True):
        selected = self.inventory.get_catch_ball(self.last_type, repeat, best)

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
