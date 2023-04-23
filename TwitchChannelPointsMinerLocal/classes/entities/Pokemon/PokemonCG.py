import random
from datetime import datetime, timedelta
import json

from .Discord import Discord
from .Missions import Missions
from .Inventory import Inventory
from .Pokedex import Pokedex
from .Pokeping import Pokeping
from .Computer import Computer

SETTINGS_FILE = "pokemon.json"

WONDERTRADE_DELAY = 60 * 60 * 3 + 60  # 3 hours and 1 min (just in case)
POKEDAILY_DELAY = 60 * 60 * 20 + 60  # 20 hours and 1 min


class PokemonComunityGame(object):
    def __init__(self):
        self.delay = 0
        self.reset_timer()
        self.wondertrade_timer = None
        self.pokedaily_timer = None
        self.last_random = None

        self.channel_list = []

        self.settings = {
            "catch_everything": False,
            "catch_alternates": False,
            "complete_bag": False,
            "catch": [],
            "catch_tiers": [],
            "catch_types": []
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

        dexneed = self.pokedex.need(pokemon)
        if dexneed in [True, None]:
            reasons.append("pokedex")
            if dexneed is None:
                reasons.append("pokedex_error")

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

        for poke_type in pokemon.types:
            if poke_type in self.settings["catch_types"]:
                reasons.append("type")
                break

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

    # ########### Channels ############

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

    # ########### Wondertrade ############

    def reset_wondertrade_timer(self):
        self.wondertrade_timer = datetime.utcnow()

    def check_wondertrade(self):
        if self.wondertrade_timer is None:
            return False

        if (datetime.utcnow() - self.wondertrade_timer).total_seconds() > WONDERTRADE_DELAY:
            return True

        return False

    def check_wondertrade_left(self):
        return timedelta(seconds=WONDERTRADE_DELAY) - (datetime.utcnow() - self.wondertrade_timer)

    # ########### Pokedaily ############

    def reset_pokedaily_timer(self):
        self.pokedaily_timer = datetime.utcnow()

    def check_pokedaily(self):
        if self.pokedaily_timer is None:
            return False

        if (datetime.utcnow() - self.pokedaily_timer).total_seconds() > POKEDAILY_DELAY:
            return True

        return False

    def check_pokedaily_left(self):
        return timedelta(seconds=POKEDAILY_DELAY) - (datetime.utcnow() - self.pokedaily_timer)
