import random
from datetime import datetime
import json

from .Discord import Discord
from .Missions import Missions
from .Inventory import Inventory
from .Pokedex import Pokedex
from .Pokeping import Pokeping
from .Computer import Computer

SETTINGS_FILE = "pokemon.json"

WONDERTRADE_DELAY = 60 * 60 * 3 + 60  # 3 hours and 1 min (just in case)
BALANCE_TRIGGER = 1
ITEM_MIN_AMOUNT = 30
ITEM_MIN_PURCHASE = 10
ITEM_PRIORITY = ["pokeball", "ultraball"]
ITEM_PRICES = {
    "pokeball": 300,
    "greatball": 600,
    "ultraball": 1000,
}

"""
Todo:
    Mission parsing using api
    re-implement buying balls when need
    pokedaily
"""


class PokemonComunityGame(object):
    def __init__(self):
        self.delay = 0
        self.reset_timer()
        self.wondertrade_timer = None
        self.last_random = None

        self.channel_list = []

        self.settings = {
            "catch_everything": False,
            "catch_alternates": False,
            "complete_bag": False,
            "catch": [],
            "catch_tiers": []
        }

        self.discord = Discord()
        self.inventory = Inventory()
        self.pokedex = Pokedex()
        self.missions = Missions()
        self.pokeping = Pokeping()
        self.computer = Computer()

        self.pokeping.set_discord(self.discord)

        self.load_settings()

        self.discord.connect()
        self.pokeping.get_roles()

    def reset_timer(self):
        self.catch_timer = datetime.utcnow()

    def reset_wondertrade_timer(self):
        self.wondertrade_timer = datetime.utcnow()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            to_write = {
                "settings": self.settings,
                "discord": self.discord.data
            }
            f.write(json.dumps(to_write, indent=4))

    def load_settings(self):
        with open(SETTINGS_FILE, "r") as f:
            j = json.load(f)
            self.set(j.get("settings", {}))
            self.discord.set(j.get("discord", {}))

    def set(self, settings):
        for k in settings:
            if k in self.settings:
                self.settings[k] = settings[k]

    def check_catch(self):
        if (datetime.utcnow() - self.catch_timer).total_seconds() > self.delay:
            return True

        return False

    def check_wondertrade(self):
        if self.wondertrade_timer is None:
            return False

        if (datetime.utcnow() - self.wondertrade_timer).total_seconds() > WONDERTRADE_DELAY:
            return True

        return False

    def sync_inventory(self, inv):
        self.inventory.set(inv)

    def sync_pokedex(self, dex):
        self.pokedex.set(dex)
        self.computer.total = self.pokedex.total

    def sync_computer(self, all_pokemon):
        self.computer.set(all_pokemon)

    def sync_missions(self, missions):
        self.missions.set(missions)

    def set_delay(self, delay):
        self.delay = delay

    def get_last_spawned(self):
        return self.pokeping.get_pokemon()

    def need_pokemon(self, pokemon):
        reasons = []
        if self.pokedex.need(pokemon):
            reasons.append("pokedex")

        if self.settings["complete_bag"]:
            if self.computer.need(pokemon):
                reasons.append("bag")

        if self.settings["catch_alternates"]:
            if pokemon.is_alternate and self.computer.need(pokemon):
                reasons.append("alt")

        missions = self.missions.check_all_missions(pokemon)
        for mission in missions:
            reasons.append(mission)

        for catch in self.settings["catch"]:
            if pokemon.name.startswith(catch):
                reasons.append("catch")

        if pokemon.tier in self.settings["catch_tiers"]:
            reasons.append("tiers")

        if self.settings["catch_everything"]:
            # catch anything:
            reasons.append("everthing")

        best_ball = False
        for reason in reasons:
            if self.missions.mission_best_ball(reason):
                best_ball = True
                break

        return reasons, best_ball

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
