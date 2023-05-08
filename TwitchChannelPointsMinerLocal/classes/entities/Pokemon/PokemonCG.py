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
LOYALTY_FILE = "pokemon_loyalty.txt"

WONDERTRADE_DELAY = 60 * 60 * 3 + 60  # 3 hours and 1 min (just in case)
POKEDAILY_DELAY = 60 * 60 * 20 + 60  # 20 hours and 1 min

FEATURED_LOYALTY = {
    1: {"limit": 25, "reward": "Earn additional 5% $"},
    2: {"limit": 50, "reward": "Chance to obtain a golden ticket"},
    3: {"limit": 100, "reward": "Catch Pokemon up to level 25"},
    4: {"limit": 200, "reward": "Increased stone drop chance by 5%"},
    5: {"limit": 300, "reward": "Chance to find rare Candy when attempting to catch Pokemon"},
    6: {"limit": 500, "reward": "+3% Higher catch chance"},
    7: {"limit": 750, "reward": "5% increased shiny chance"},
    8: {"limit": 1000, "reward": "Earn additional 5% $"},
}
LOYALTY = {
    1: {"limit": 100, "reward": "Increased stone drop chance by 5%"},
    2: {"limit": 250, "reward": "Catch Pokemon up to level 25"},
    3: {"limit": 500, "reward": "Chance to find rare Candy when attempting to catch"},
    4: {"limit": 1000, "reward": "3% increased shiny chance"}
}


class PokemonComunityGame(object):
    def __init__(self):
        self.delay = 0
        self.reset_timer()
        self.wondertrade_timer = None
        self.pokedaily_timer = None
        self.last_random = None

        self.channel_list = []
        self.loyalty_data = {}

        self.settings = {
            "catch_everything": False,
            "catch_alternates": False,
            "catch_fish": False,
            "complete_bag": False,
            "use_special_balls": True,
            "catch_starters": True,
            "catch_legendaries": True,
            "money_saving": 0,
            "catch": [],
            "catch_tiers": [],
            "catch_types": [],
            "channel_priority": [],
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
        self.inventory.use_special_balls = self.settings["use_special_balls"]

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
        pokemon = self.pokeping.get_pokemon()
        # dont need this for now because getting from pokeping
        # pokemon.is_fish = self.pokedex.fish(pokemon)
        return pokemon

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
                reasons.append("all_type")
                break

        if self.settings["catch_legendaries"] and self.pokedex.legendary(pokemon):
            reasons.append("legendary")

        if self.settings["catch_starters"] and self.pokedex.starter(pokemon):
            reasons.append("starter")

        if pokemon.tier in self.settings["catch_tiers"]:
            reasons.append("tiers")

        if self.settings["catch_fish"] and pokemon.is_fish:
            reasons.append("all_fish")

        if self.settings["catch_everything"]:
            # catch anything:
            reasons.append("everything")

        strategy = "worst"
        for reason in reasons:
            if self.missions.mission_best_ball(reason):
                strategy = "best"
                break
        if strategy == "best":
            if self.inventory.cash < self.settings["money_saving"]:
                strategy = "save"

        return reasons, strategy

    # ########### Channels ############

    def add_channel(self, channel):
        if channel not in self.channel_list:
            self.channel_list.append(channel)

    def remove_channel(self, channel):
        if channel in self.channel_list:
            self.channel_list.remove(channel)

    def get_channel(self):
        if len(self.channel_list) == 0:
            return None

        for channel in self.settings["channel_priority"]:
            if channel in self.channel_list:
                return channel

        return self.get_highest_loyalty_channel()

    def random_channel(self):
        nr_channels = len(self.channel_list)
        if nr_channels == 1:
            self.last_random = self.channel_list[0]
        else:
            self.last_random = random.choice([channel for channel in self.channel_list if channel != self.last_random])
        return self.last_random

    # ########### Channel Loyalty ############

    def set_loyalty(self, channel, loyalty_level, current_points, level_points):
        if (
            level_points == 250
        ) or (
            level_points == 100 and loyalty_level == 1
        ) or (
            level_points == 500 and loyalty_level == 3
        ) or (
            level_points == 1000 and loyalty_level == 4
        ):
            featured_channel = False
        else:
            featured_channel = True

        self.loyalty_data[channel] = {
            "featured": featured_channel,
            "level": loyalty_level,
            "points": current_points,
            "limit": level_points
        }

        self.output_loyalty()

    def get_loyalty(self, level, featured):
        loyalty_data = FEATURED_LOYALTY if featured else LOYALTY
        return loyalty_data.get(level, None)

    def get_highest_loyalty_channel(self):
        if len(self.loyalty_data.keys()) == 0:
            return None

        all_channels = sorted(
            [(key, values) for key, values in self.loyalty_data.items()],
            key=lambda x: (not x[1]["featured"], 0 - x[1]["points"])
        )

        return all_channels[0][0]

    def increment_loyalty(self, channel):
        to_return = None

        if channel in self.loyalty_data:
            self.loyalty_data[channel]["points"] = self.loyalty_data[channel]["points"] + 1
            if self.loyalty_data[channel]["points"] == self.loyalty_data[channel]["limit"]:
                loyalty = FEATURED_LOYALTY if self.loyalty_data[channel]["featured"] else LOYALTY
                current_reward = loyalty[self.loyalty_data[channel]["level"]]["reward"]

                self.loyalty_data[channel]["level"] = self.loyalty_data[channel]["level"] + 1
                if self.loyalty_data[channel]["level"] in loyalty:
                    next_level = loyalty[self.loyalty_data[channel]["level"]]
                    self.loyalty_data[channel]["limit"] = next_level["limit"]
                    next_reward = next_level["reward"]
                else:
                    self.loyalty_data[channel]["limit"] = None
                    next_reward = None
                to_return = [current_reward, next_reward]

            self.output_loyalty()

        return to_return

    def output_loyalty(self):
        to_output = sorted(
            [(key, values) for key, values in self.loyalty_data.items()],
            key=lambda x: (not x[1]["featured"], 0 - x[1]["points"])
        )
        with open(LOYALTY_FILE, "w") as output:
            for channel, data in to_output:
                featured = "*" if data["featured"] else ""
                level = data["level"]
                points = data["points"]
                limit = data["limit"]
                output.write(f"{featured}{channel} - level {level} - {points}/{limit}\n")

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
