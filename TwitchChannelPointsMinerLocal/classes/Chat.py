from datetime import datetime, timedelta
from time import sleep
from dateutil.parser import parse
import random
import logging
from threading import Thread
import traceback

from .ChatO import ClientIRC as ClientIRCO
from .ChatO import ChatPresence as ChatPresenceO
from .ChatO import ThreadChat as ThreadChatO
from .ChatO import logger

from .entities.Pokemon import PokemonComunityGame, CGApi, Pokedaily, Pokemon, get_sprite

""" TODO
- add call to timer to get pokemon id more confidently
    this will allow to move from depending on pokeping for IDs
- battle system
"""

formatter = logging.Formatter('%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler("logs/pokemoncg.txt", encoding='utf-8')
file_handler.setFormatter(formatter)
poke_logger = logging.getLogger(__name__ + "pokemon")
poke_logger.setLevel(logging.DEBUG)
poke_logger.addHandler(file_handler)

POKEMON_CHECK_DELAY = 30  # seconds
POKEMON_CHECK_DELAY_RELAX = 60 * 14  # 14 mins
POKEMON_CHECK_LIMIT_MAX = 75  # pokemon is valid for 75 seconds after spawning
POKEMON_CHECK_LIMIT_MIN = 10  # pokemon is valid 10 seconds after spawning

ITEM_MIN_AMOUNT = 10
ITEM_MIN_PURCHASE = 10

MARBLES_DELAY = 60 * 3  # seconds
MARBLES_TRIGGER_COUNT = 3

REDLOG = "\x1b[31;20m"
GREENLOG = "\x1b[32;20m"
YELLOWLOG = "\x1b[36;20m"

ALERTS_CHANNEL = 1072557550526013440
POKEDAILY_CHANNEL = 800433942695247872
POKEDAILY_GUILD = 711921837503938640

POKEMON = PokemonComunityGame()

DISCORD_BASE = "https://discord.com/api/v9/"
DISCORD_ALERTS = f"{DISCORD_BASE}channels/{ALERTS_CHANNEL}/messages"
DISCORD_POKEDAILY = f"{DISCORD_BASE}channels/{POKEDAILY_CHANNEL}/messages"
DISCORD_POKEDAILY_SEARCH = f"{DISCORD_BASE}guilds/{POKEDAILY_GUILD}/messages/search?channel_id={POKEDAILY_CHANNEL}&mentions=" + "{discord_id}"

FISH_EVENT = True


class ThreadController(object):
    def __init__(self):
        self.client_channel = None
        self.client = None
        self.wondertrade = False
        self.pokecatch = False
        self.pokedaily = False
        self.bag_stats = False


THREADCONTROLLER = ThreadController()

CHARACTERS = {
    "starter": "⭐",
    "female": "♀",
    "legendary": "💪"
}


def seconds_readable(seconds):
    return str(timedelta(seconds=seconds)).split(".")[0]


def create_thread(func):
    worker = Thread(target=func)
    worker.setDaemon(True)
    worker.start()


def timer_thread(func):
    def pokemon_timer():

        remaining_human = seconds_readable(POKEMON.delay)
        logger.info(f"{YELLOWLOG}Waiting for {remaining_human}", extra={"emoji": ":speech_balloon:"})
        sleep(POKEMON.delay)

        try:
            if THREADCONTROLLER.client is not None:
                func(THREADCONTROLLER.client)
        except KeyboardInterrupt:
            return
        except Exception as ex:
            str_ex = str(ex)
            logger.info(f"{REDLOG}Timer func failed - {str_ex}", extra={"emoji": ":speech_balloon:"})
            THREADCONTROLLER.client = None
            POKEMON.delay = 5
            print(traceback.format_exc())

            if len(POKEMON.channel_list) == 0:
                THREADCONTROLLER.pokecatch = False

        if THREADCONTROLLER.pokecatch:
            create_thread(pokemon_timer)

    if THREADCONTROLLER.pokecatch is False:
        THREADCONTROLLER.pokecatch = True
        create_thread(pokemon_timer)


def wondertrade_thread(func):
    max_wait = 60 * 60  # 1 hour

    def wondertrade_timer():
        if POKEMON.wondertrade_timer is None:
            remaining = 5
        else:
            remaining = POKEMON.check_wondertrade_left().total_seconds()

        remaining_human = seconds_readable(remaining)
        logger.info(f"{YELLOWLOG}Waiting for {remaining_human}", extra={"emoji": ":speech_balloon:"})

        sleep(min(remaining, max_wait))
        if remaining <= max_wait:
            try:
                func()
            except KeyboardInterrupt:
                return
            except Exception as ex:
                str_ex = str(ex)
                logger.info(f"{REDLOG}Wondertrade func failed - {str_ex}", extra={"emoji": ":speech_balloon:"})
                POKEMON.wondertrade_timer = None
                print(traceback.format_exc())

                if len(POKEMON.channel_list) == 0:
                    THREADCONTROLLER.wondertrade = False

        create_thread(wondertrade_timer)

    if THREADCONTROLLER.wondertrade is False:
        THREADCONTROLLER.wondertrade = True
        create_thread(wondertrade_timer)


def pokedaily_thread(func):
    max_wait = 60 * 60  # 1 hour

    def pokedaily_timer():
        if POKEMON.pokedaily_timer is None:
            remaining = 5
        else:
            remaining = POKEMON.check_pokedaily_left().total_seconds()

        remaining_human = seconds_readable(remaining)
        logger.info(f"{YELLOWLOG}Waiting for {remaining_human}", extra={"emoji": ":speech_balloon:"})

        sleep(min(remaining, max_wait))
        if remaining <= max_wait:
            func()

        create_thread(pokedaily_timer)

    if THREADCONTROLLER.pokedaily is False:
        THREADCONTROLLER.pokedaily = True
        create_thread(pokedaily_timer)


def bag_stats_thread(func):
    def bag_stats_timer():
        previous = None
        while True:
            cur_date = datetime.now().date()
            if cur_date != previous:
                func()
                previous = cur_date
            sleep(60 * 15)  # 15 mins

    if THREADCONTROLLER.bag_stats is False:
        THREADCONTROLLER.bag_stats = True
        create_thread(bag_stats_timer)


class ClientIRCBase(ClientIRCO):
    def __init__(self, username, token, channel):
        ClientIRCO.__init__(self, username, token, channel)

    @staticmethod
    def log(msg):
        logger.info(msg, extra={"emoji": ":speech_balloon:"})


class ClientIRCMarbles(ClientIRCBase):
    def __init__(self, username, token, channel, marbles):
        ClientIRCBase.__init__(self, username, token, channel)
        self.init(marbles)

    def init(self, marbles):
        self.marbles = marbles
        self.marbles_timer = datetime.utcnow()
        self.marbles_counter = 0

    def on_pubmsg(self, client, message):
        if self.marbles and "!play" in " ".join(message.arguments):
            self.check_marbles(client, message)

    def check_marbles(self, client, message):
        now = datetime.utcnow()
        if (now - self.marbles_timer).total_seconds() > MARBLES_DELAY:
            self.marbles_timer = now
            self.marbles_counter = 0

        self.marbles_counter += 1

        if self.marbles_counter == MARBLES_TRIGGER_COUNT:
            sleep(random.randint(0, 60))
            client.privmsg(message.target, "!play")
            self.log(f"Joined Marbles for {message.target[1:]}")


class ClientIRCPokemon(ClientIRCBase):
    def __init__(self, username, token, channel, get_pokemon_token):
        ClientIRCBase.__init__(self, username, token, channel)
        self.init(username, get_pokemon_token)

    def init(self, username, get_pokemon_token):
        self.username = username.lower()
        self.at_username = "@" + self.username

        self.pokemon_active = False
        self.pokemon_disabled = False
        self.pokemon_api = CGApi()
        self.pokemon_api.get_auth_token = get_pokemon_token

    @staticmethod
    def log_file(msg):
        poke_logger.info(msg)

    def die(self):
        self.pokemon_active = False
        self.pokemon_disabled = False

    def on_pubmsg(self, client, message):
        argstring = " ".join(message.arguments)

        if "pokemoncommunitygame" in message.source:
            self.check_pokemon_active(client, message, argstring)
            self.check_loyalty_info(client, message, argstring)

        if THREADCONTROLLER.client is None:
            THREADCONTROLLER.client = client
            THREADCONTROLLER.client_channel = self.channel[1:]
            self.log(f"{YELLOWLOG}{self.channel[1:]} is primary client")

        if len(POKEMON.channel_list) > 0:
            if THREADCONTROLLER.pokecatch is False:
                timer_thread(self.check_main)
            if THREADCONTROLLER.wondertrade is False:
                wondertrade_thread(self.wondertrade_main)
            if THREADCONTROLLER.pokedaily is False:
                pokedaily_thread(self.pokedaily_main)
            if THREADCONTROLLER.bag_stats is False:
                bag_stats_thread(self.stats_computer)

    def check_loyalty_info(self, client, message, argstring):
        if self.username in argstring and "Your loyalty level" in argstring:
            channel = message.target[1:]
            loyalty_level = int(argstring.split("Your loyalty level: ")[1][0])
            loyalty_limits = argstring.split("(")[1].split(")")[0]
            current_points = int(loyalty_limits.split("/")[0])
            level_points = int(loyalty_limits.split("/")[1])
            self.log(f"{YELLOWLOG}{channel} loyalty {current_points}/{level_points}, level {loyalty_level}")

            POKEMON.set_loyalty(channel, loyalty_level, current_points, level_points)

    def check_pokemon_active(self, client, message, argstring):
        if "Spawns and payouts are disabled" in argstring:
            if self.pokemon_disabled is False:
                self.pokemon_disabled = True
                self.pokemon_active = False
                logger.info(f"Pokemon Disabled: {self.channel}", extra={"emoji": ":speech_balloon:"})
                leave_channel(self.channel[1:])

        elif self.pokemon_active is False:
            if self.pokemon_disabled is False or (" has been caught by:" in argstring or " escaped." in argstring):
                self.pokemon_active = True
                self.pokemon_disabled = False
                self.log(f"{YELLOWLOG}Joined Pokemon for {message.target[1:]}")
                POKEMON.add_channel(self.channel[1:])
                sleep(5)
                self.log(f"{YELLOWLOG}{self.channel[1:]} loyalty request")
                client.privmsg("#" + self.channel[1:], "!pokeloyalty")

    def pokedaily_main(self):
        POKEMON.discord.post(DISCORD_POKEDAILY, "!pokedaily")

        if POKEMON.discord.data["user"] is None:
            POKEMON.discord.post(DISCORD_ALERTS, "Pokedaily, no user configured")
            self.log(f"{GREENLOG}Pokedaily, no user configured")
            return

        sleep(60 * 2)
        resp = POKEMON.discord.get(DISCORD_POKEDAILY_SEARCH.format(discord_id=POKEMON.discord.data["user"]))
        content = resp["messages"][0][0]["content"]
        message = Pokedaily.parse_message(content)

        if message.repeat:
            last_redeemed = timedelta(
                hours=message.last_redeemed["hours"],
                minutes=message.last_redeemed["minutes"],
                seconds=message.last_redeemed["seconds"]
            )

            self.log(f"{REDLOG}Pokedaily not ready")
            POKEMON.pokedaily_timer = datetime.utcnow() - last_redeemed

        else:
            POKEMON.reset_pokedaily_timer()
            POKEMON.discord.post(DISCORD_ALERTS, f"Pokedaily rewards ({message.rarity}):\n" + "\n".join(message.rewards))
            self.log(f"{GREENLOG}Pokedaily ({message.rarity}) rewards " + ", ".join(message.rewards))

    def wondertrade_main(self):
        self.get_missions()
        self.sort_computer()
        self.check_wondertrade()
        self.get_missions()

    def check_wondertrade(self):
        allpokemon = POKEMON.computer.pokemon
        if len(allpokemon) > 0:

            if POKEMON.wondertrade_timer is None:
                # get the timer from a pokemon
                pokemon = self.pokemon_api.get_pokemon(allpokemon[0]["id"])

                can_trade_in = pokemon["tradable"]
                if can_trade_in is None:
                    POKEMON.wondertrade_timer = datetime.utcnow() - timedelta(hours=4)
                else:
                    if "hour" in can_trade_in:
                        hours = 2 - int(can_trade_in.split(" ")[0])
                    else:
                        hours = 2
                    if "minute" in can_trade_in:
                        minutes = 60 - int(can_trade_in.split(" ")[-2])
                    else:
                        minutes = 60

                    if minutes == 60:
                        minutes = 0
                        hours = hours + 1

                    POKEMON.wondertrade_timer = datetime.utcnow() - timedelta(minutes=minutes, hours=hours)

            if POKEMON.check_wondertrade():
                dex = self.pokemon_api.get_pokedex()
                POKEMON.sync_pokedex(dex)

                tradable = [pokemon for pokemon in allpokemon if pokemon["nickname"] is not None and "trade" in pokemon["nickname"]]
                checks = [POKEMON.missions.have_wondertrade_missions()]
                pokemon_to_trade = []
                reasons = []

                if checks[0] == True:
                    checks.append(False)

                for missions_active in checks:
                    for tier in ["A", "B", "C"]:
                        if len(pokemon_to_trade) > 0:
                            break

                        looking_for = f"trade{tier}"
                        for pokemon in tradable:
                            if looking_for in pokemon["nickname"]:
                                if missions_active:
                                    pokedex_entry = self.pokemon_api.get_pokedex_info(pokemon["pokedexId"])["content"]
                                    sleep(0.5)

                                    pokemon_object = Pokemon()
                                    pokemon_object.types = [pokedex_entry["type1"].title(), pokedex_entry["type2"].title()]
                                    pokemon_object.bst = sum([pokedex_entry["base_stats"][k] for k in pokedex_entry["base_stats"]])
                                    pokemon_object.is_fish = POKEMON.pokedex.fish(pokemon["name"])

                                    reasons = POKEMON.missions.check_all_wondertrade_missions(pokemon_object)
                                    if len(reasons) == 0:
                                        continue
                                pokemon_to_trade.append(pokemon)
                                if missions_active:
                                    # if missions are active and find pokemon just take it to not spam api
                                    break

                if len(pokemon_to_trade) == 0:
                    self.log(f"{REDLOG}Could not find a pokemon to wondertrade")
                else:
                    sorted_pokemon_to_trade = sorted(pokemon_to_trade, key=lambda x: x["sellPrice"])

                    # pokemon_traded = random.choice(pokemon_to_trade)
                    pokemon_traded = sorted_pokemon_to_trade[0]
                    pokemon_received = self.pokemon_api.wondertrade(pokemon_traded["id"])

                    if "pokemon" in pokemon_received:
                        pokemon_received = pokemon_received["pokemon"]
                        pokemon_traded_tier = POKEMON.pokedex.tier(pokemon_traded["name"])
                        pokemon_received_tier = POKEMON.pokedex.tier(pokemon_received["name"])

                        if POKEMON.pokedex.have(pokemon_received["name"]):
                            pokemon_received_need = ""
                            pokemon_sprite = None
                        else:
                            pokemon_received_need = " - needed"
                            sprite = str(pokemon_received["pokedexId"])
                            pokemon_sprite = get_sprite("pokemon", sprite, shiny=pokemon_received["isShiny"])

                        reasons_string = "" if len(reasons) == 0 else " ({})".format(", ".join(reasons))

                        wondertrade_msg = f"Wondertraded {pokemon_traded['name']} ({pokemon_traded_tier}){reasons_string} for {pokemon_received['name']} ({pokemon_received_tier}){pokemon_received_need}"
                        self.log(f"{GREENLOG}{wondertrade_msg}")
                        POKEMON.discord.post(DISCORD_ALERTS, wondertrade_msg, file=pokemon_sprite)
                        POKEMON.reset_wondertrade_timer()
                    else:
                        self.log(f"{REDLOG}Wondertrade {pokemon_traded['name']} failed {pokemon_received}")
                        POKEMON.wondertrade_timer = None
            else:
                time_remaining = POKEMON.check_wondertrade_left()
                time_str = str(time_remaining).split(".")[0]
                self.log(f"{YELLOWLOG}Wondertrade available in {time_str}")
        else:
            POKEMON.wondertrade_timer = None

    def stats_computer(self):

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        dex = self.pokemon_api.get_pokedex()
        POKEMON.sync_pokedex(dex)

        inv = self.pokemon_api.get_inventory()
        POKEMON.sync_inventory(inv)

        allpokemon = POKEMON.computer.pokemon

        spawnables = [pokemon for pokemon in POKEMON.pokedex.pokemon if (POKEMON.pokedex.starter(pokemon) or POKEMON.pokedex.legendary(pokemon)) is False]
        spawnables_a = []
        spawnables_b = []
        spawnables_c = []

        for pokemon in spawnables:
            t = POKEMON.pokedex.tier(pokemon)
            if t == "A":
                spawnables_a.append(pokemon)
            elif t == "B":
                spawnables_b.append(pokemon)
            elif t == "C":
                spawnables_c.append(pokemon)

        spawnables_total = len(spawnables)
        spawnables_a_total = len(spawnables_a)
        spawnables_b_total = len(spawnables_b)
        spawnables_c_total = len(spawnables_c)

        spawnables_a_have = len([pokemon for pokemon in spawnables_a if POKEMON.pokedex.have(pokemon)])
        spawnables_b_have = len([pokemon for pokemon in spawnables_b if POKEMON.pokedex.have(pokemon)])
        spawnables_c_have = len([pokemon for pokemon in spawnables_c if POKEMON.pokedex.have(pokemon)])
        spawnables_a_dont_have = [pokemon for pokemon in spawnables_a if POKEMON.pokedex.have(pokemon) is False]
        spawnables_b_dont_have = [pokemon for pokemon in spawnables_b if POKEMON.pokedex.have(pokemon) is False]
        spawnables_c_dont_have = [pokemon for pokemon in spawnables_c if POKEMON.pokedex.have(pokemon) is False]
        spawnables_have = spawnables_a_have + spawnables_b_have + spawnables_c_have

        spawnables_per = int(spawnables_have * 10000.0 / spawnables_total) / 100.0
        spawnables_a_per = int(spawnables_a_have * 10000.0 / spawnables_a_total) / 100.0
        spawnables_b_per = int(spawnables_b_have * 10000.0 / spawnables_b_total) / 100.0
        spawnables_c_per = int(spawnables_c_have * 10000.0 / spawnables_c_total) / 100.0

        results = {
            "shiny": len([pokemon for pokemon in allpokemon if pokemon["isShiny"]]),
            "starter": len(set([pokemon["pokedexId"] for pokemon in allpokemon if POKEMON.pokedex.starter(pokemon["name"])])),
            "female": len(set([pokemon["pokedexId"] for pokemon in allpokemon if POKEMON.pokedex.female(pokemon["pokedexId"])])),
            "legendary": len(set([pokemon["pokedexId"] for pokemon in allpokemon if POKEMON.pokedex.legendary(pokemon["name"])])),
            "bag_regular": len(set([pokemon["pokedexId"] for pokemon in allpokemon if pokemon["pokedexId"] <= POKEMON.pokedex.total])),
            "bag_special": len(set([pokemon["pokedexId"] for pokemon in allpokemon if pokemon["pokedexId"] > POKEMON.pokedex.total])),
        }

        for tier in ["S", "A", "B", "C"]:
            results[f"trade{tier}"] = len([pokemon for pokemon in allpokemon if pokemon["nickname"] is not None and f"trade{tier}" in pokemon["nickname"]])

        region_msg_list = []
        prefixes = POKEMON.pokedex.prefixes
        for region in prefixes:
            num = len(set([pokemon["pokedexId"] for pokemon in allpokemon if pokemon["name"].startswith(prefixes[region] + " ")]))
            if num > 0:
                region_msg_list.append((region, num))

        region_msg = "".join([f"\n    {region}: {num}" for region, num in region_msg_list])

        tradable_total = sum([results[f"trade{tier}"] for tier in ["A", "B", "C"]])

        cash = POKEMON.inventory.cash
        pokeball = POKEMON.inventory.balls.get("pokeball", 0)
        premierball = POKEMON.inventory.balls.get("premierball", 0)
        greatball = POKEMON.inventory.balls.get("greatball", 0)
        ultraball = POKEMON.inventory.balls.get("ultraball", 0)
        otherball = sum([value for key, value in POKEMON.inventory.balls.items() if key not in ["pokeball", "premierball", "greatball", "ultraball"]])
        coins = 0
        for item in POKEMON.inventory.items:
            if item["name"].lower() == "battle coin":
                coins = item["amount"]
                break

        if len(spawnables_a_dont_have) == 0:
            missing_a_string = "Done"
        else:
            missing_a_string = "missing: " + ", ".join(spawnables_a_dont_have) if len(spawnables_a_dont_have) in range(0, 10) else ""

        if len(spawnables_b_dont_have) == 0:
            missing_b_string = "Done"
        else:
            missing_b_string = "missing: " + ", ".join(spawnables_b_dont_have) if len(spawnables_b_dont_have) in range(0, 10) else ""

        if len(spawnables_c_dont_have) == 0:
            missing_c_string = "Done"
        else:
            missing_c_string = "missing: " + ", ".join(spawnables_c_dont_have) if len(spawnables_c_dont_have) in range(0, 10) else ""

        discord_msg = f"""Bag Summary:

Starters: {results["starter"]}/{POKEMON.pokedex.starters}
Legendary: {results["legendary"]}/{POKEMON.pokedex.legendaries}
Shiny: {results["shiny"]}

Normal Version: {results["bag_regular"]}/{POKEMON.pokedex.total}
Alt Version: {results["bag_special"]}
    {CHARACTERS["female"]}: {results["female"]}/{POKEMON.pokedex.females}{region_msg}

Spawnables: {spawnables_have}/{spawnables_total} ({spawnables_per}%)
    A: {spawnables_a_have}/{spawnables_a_total} ({spawnables_a_per}%) {missing_a_string}
    B: {spawnables_b_have}/{spawnables_b_total} ({spawnables_b_per}%) {missing_b_string}
    C: {spawnables_c_have}/{spawnables_c_total} ({spawnables_c_per}%) {missing_c_string}

Tradables: {tradable_total}
    A: {results["tradeA"]}
    B: {results["tradeB"]}
    C: {results["tradeC"]}

Inventory: {cash}$ {coins} Battle Coins
    pokeball: {pokeball}
    premierball: {premierball}
    greatball: {greatball}
    ultraball: {ultraball}
    other: {otherball}
        """

        POKEMON.discord.post(DISCORD_ALERTS, discord_msg)

    def sort_computer(self):

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        allpokemon = POKEMON.computer.pokemon
        pokedict = {}
        shineys = []
        changes = []

        for pokemon in allpokemon:
            if pokemon["isShiny"]:
                shineys.append(pokemon)
            else:
                pokedict.setdefault(pokemon["pokedexId"], []).append(pokemon)

        for pokeid in pokedict.keys():
            ordered = sorted(pokedict[pokeid], key=lambda x: (-x["avgIV"], -x["lvl"]))
            for index, pokemon in enumerate(ordered):
                if pokemon["nickname"] is not None:
                    if "trade" not in pokemon["nickname"]:
                        tempnick = pokemon["nickname"]
                        for character in CHARACTERS.values():
                            tempnick = tempnick.replace(character, "")
                        if tempnick != pokemon["name"]:
                            continue
                if index == 0:
                    if POKEMON.pokedex.starter(pokemon["name"]):
                        nick = CHARACTERS["starter"] + pokemon["name"]
                    elif POKEMON.pokedex.legendary(pokemon["name"]):
                        nick = CHARACTERS["legendary"] + pokemon["name"]
                    elif POKEMON.pokedex.female(pokemon["pokedexId"]):
                        nick = pokemon["name"] + CHARACTERS["female"]
                    elif pokemon["nickname"] is None or pokemon["nickname"].startswith("trade") is False:
                        # if not starter and not female and has nickname, dont mess
                        continue
                    else:
                        nick = ""
                else:
                    tier = POKEMON.pokedex.tier(pokemon["name"])
                    if tier is None:
                        nick = "trade?"
                    else:
                        nick = "trade" + tier
                    if POKEMON.pokedex.starter(pokemon["name"]):
                        nick = CHARACTERS["starter"] + nick
                    elif POKEMON.pokedex.legendary(pokemon["name"]):
                        nick = CHARACTERS["legendary"] + nick
                    elif POKEMON.pokedex.female(pokemon["pokedexId"]):
                        nick = nick + CHARACTERS["female"]

                if pokemon["nickname"] == nick:
                    continue
                changes.append((pokemon["id"], nick, pokemon["name"], pokemon["nickname"]))

        for pokemon in shineys:
            if pokemon["nickname"] is not None:
                changes.append((pokemon["id"], "", pokemon["name"], pokemon["nickname"]))

        for poke_id, new_name, real_name, old_name in changes:
            if new_name is not None and len(new_name) > 12:
                self.log_file(f"{YELLOWLOG}Wont rename {real_name} from {old_name} to {new_name}, name too long")
                continue
            self.pokemon_api.set_name(poke_id, new_name)
            self.log_file(f"{YELLOWLOG}Renamed {real_name} from {old_name} to {new_name}")
            sleep(0.5)

    def check_inventory(self):
        inv = self.pokemon_api.get_inventory()
        POKEMON.sync_inventory(inv)

        shop = self.pokemon_api.get_shop()
        shop_balls = []
        for item in shop["shopItems"]:
            if item["category"] == "ball":
                shop_balls.append(item)

        changes = False
        for ball in sorted(shop_balls, key=lambda x: x["price"]):
            ball_name = ball["displayName"].lower().replace(" ", "")
            ball_have = POKEMON.inventory.balls.get(ball_name, 0)
            if ball_have < ITEM_MIN_AMOUNT:
                can_afford = POKEMON.inventory.cash // ball["price"] // ITEM_MIN_PURCHASE * ITEM_MIN_PURCHASE
                need = ((ITEM_MIN_AMOUNT - ball_have) // ITEM_MIN_PURCHASE + min((ITEM_MIN_AMOUNT - ball_have) % ITEM_MIN_PURCHASE, 1)) * ITEM_MIN_PURCHASE
                buying = min(need, can_afford)

                if buying > 0:
                    changes = True
                    resp = self.pokemon_api.buy_item(ball["name"], buying)
                    if "cash" in resp:
                        POKEMON.inventory.cash = resp["cash"]
                        self.log(f"{GREENLOG}Purchased {buying} {ball['displayName']}s")

        if changes:
            inv = self.pokemon_api.get_inventory()
            POKEMON.sync_inventory(inv)

    def get_missions(self):
        missions = self.pokemon_api.get_missions()
        POKEMON.sync_missions(missions)

        completed = POKEMON.missions.get_completed()
        for title, reward in completed:
            readable_reward = reward["reward"]
            reward_sprite = get_sprite(reward["reward_type"], reward["reward_name"])
            mission_msg = f"Completed mission - {title} - reward: {readable_reward}"
            self.log(f"{GREENLOG}{mission_msg}")
            POKEMON.discord.post(DISCORD_ALERTS, mission_msg, file=reward_sprite)
            if reward_sprite is not None:
                reward_sprite.close()

    def check_main(self, client):
        POKEMON.reset_timer()
        self.log_file(f"{YELLOWLOG}Checking pokemon spawn in pokeping")
        pokemon = POKEMON.get_last_spawned()

        spawned_seconds = (datetime.utcnow() - pokemon.spawn).total_seconds()

        if spawned_seconds <= POKEMON_CHECK_LIMIT_MAX and spawned_seconds >= POKEMON_CHECK_LIMIT_MIN:
            # pokemon spawned recently relax and process it
            POKEMON.delay = POKEMON_CHECK_DELAY_RELAX
            self.log_file(f"{YELLOWLOG}Pokemon spawned - processing {pokemon}")

            # sync everything
            dex = self.pokemon_api.get_pokedex()
            POKEMON.sync_pokedex(dex)

            all_pokemon = self.pokemon_api.get_all_pokemon()
            POKEMON.sync_computer(all_pokemon)

            self.check_inventory()

            self.get_missions()

            # find reasons to catch the pokemon
            catch_reasons, strategy = POKEMON.need_pokemon(pokemon)
            repeat = True

            for reason in ["pokedex", "bag", "alt"]:
                if reason in catch_reasons:
                    repeat = False
                    break

            if "ball" in catch_reasons:
                if strategy == "worst":
                    for catch_ball in POKEMON.missions.data["ball"]:
                        if POKEMON.inventory.have_ball(catch_ball + "ball"):
                            ball = catch_ball + "ball"
                            strategy = "force"
                            break

            if len(catch_reasons) > 0:
                if strategy != "force":
                    ball = POKEMON.inventory.get_catch_ball(pokemon, repeat=repeat, strategy=strategy)

                if ball is None:
                    self.log_file(f"{REDLOG}Won't catch {pokemon.name} ran out of balls (strategy: {strategy})")
                else:
                    twitch_channel = POKEMON.get_channel()
                    message = f"!pokecatch {ball}"
                    client.privmsg("#" + twitch_channel, message)

                    reasons_string = ", ".join(catch_reasons)
                    self.log_file(f"{GREENLOG}Trying to catch {pokemon.name} with {ball} because {reasons_string}")

                    sleep(5)

                    all_pokemon = self.pokemon_api.get_all_pokemon()
                    POKEMON.sync_computer(all_pokemon)

                    # find all the pokemon that are the current one that spawned
                    filtered = POKEMON.computer.get_pokemon(pokemon)
                    caught = None
                    for poke in filtered:
                        if (datetime.utcnow() - parse(poke["caughtAt"][:-1])).total_seconds() < 60 * 5:
                            caught = poke
                            break

                    discord_pokemon_name = pokemon.name if pokemon.is_alternate is False else pokemon.alt_name
                    rewards = None
                    self.log(f"{GREENLOG}Trying to catch in {twitch_channel}")
                    if caught is not None:
                        ivs = int(poke["avgIV"])
                        lvl = poke['lvl']
                        shiny = " Shiny" if poke["isShiny"] else ""
                        self.log_file(f"{GREENLOG}Caught{shiny} {pokemon.name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV")
                        msg = f"I caught a{shiny} {discord_pokemon_name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV!"
                        if pokemon.is_fish and FISH_EVENT:
                            caught_pokemon = self.pokemon_api.get_pokemon(poke["id"])
                            if "🐟" in caught_pokemon["description"]:
                                msg += "\n" + caught_pokemon["description"].split("Your fish is ")[-1].split("Your fish has ")[-1]

                        sprite = str(poke["pokedexId"])
                        pokemon_sprite = get_sprite("pokemon", sprite, shiny=poke["isShiny"])
                        rewards = POKEMON.increment_loyalty(twitch_channel)
                    else:
                        self.log_file(f"{REDLOG}Failed to catch {pokemon.name}")
                        msg = f"I missed {discord_pokemon_name}!"
                        pokemon_sprite = None

                    msg = msg + f" {ball}, because {reasons_string}"

                    POKEMON.discord.post(DISCORD_ALERTS, msg, file=pokemon_sprite)

                    if rewards is not None:
                        reward, next_reward = rewards
                        rewards_msg = f"Loyalty tier completed in {twitch_channel}, new reward: {reward}"
                        self.log(f"{GREENLOG}{rewards_msg}")
                        if next_reward is not None:
                            rewards_msg = rewards_msg + f"\nNext reward: {next_reward}"
                            self.log(f"{GREENLOG}next reward: {next_reward}")
                        sprite = get_sprite("streamer", twitch_channel)
                        POKEMON.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)
            else:
                self.log_file(f"{REDLOG}Don't need pokemon, skipping")

                twitch_channel = POKEMON.get_channel(ignore_priority=False)
                client.privmsg("#" + twitch_channel, "!pokecheck")
                self.log(f"{GREENLOG}Pokecheck in {twitch_channel}")

            self.get_missions()
        elif spawned_seconds <= POKEMON_CHECK_LIMIT_MAX:
            # pokemon spawned but its too new, make sure pokeping sends all messages
            POKEMON.delay = POKEMON_CHECK_LIMIT_MIN
            self.log_file(f"{YELLOWLOG}Pokemon spawed, waiting to see if is alt")
        else:
            # pokemon should be spawning soon
            POKEMON.delay = POKEMON_CHECK_DELAY
            self.log_file(f"{YELLOWLOG}Pokemon spawning soon")


class ClientIRC(ClientIRCMarbles, ClientIRCPokemon):
    def __init__(self, username, token, channel, get_pokemoncg_token, marbles):
        ClientIRCMarbles.__init__(self, username, token, channel, marbles)
        ClientIRCPokemon.init(self, username, get_pokemoncg_token)

    def on_pubmsg(self, client, message):
        ClientIRCMarbles.on_pubmsg(self, client, message)
        ClientIRCPokemon.on_pubmsg(self, client, message)

    def die(self, msg="Bye, cruel world!"):
        ClientIRCPokemon.die(self)
        self.connection.disconnect(msg)
        self.__active = False


class ThreadChat(ThreadChatO):
    def __init__(self, username, token, channel, channel_id, get_pokemoncg_token, marbles):
        ThreadChatO.__init__(self, username, token, channel)
        self.marbles = marbles
        self.channel_id = channel_id
        self.get_pokemoncg_token_func = get_pokemoncg_token

    def get_pokemoncg_token(self):
        return self.get_pokemoncg_token_func(self.channel_id)

    def run(self):
        self.chat_irc = ClientIRC(
            self.username,
            self.token,
            self.channel,
            self.get_pokemoncg_token,
            self.marbles
        )
        logger.info(
            f"Join IRC Chat: {self.channel}", extra={"emoji": ":speech_balloon:"}
        )
        POKEMON.channel_online(self.channel)
        self.chat_irc.start()

    def stop(self):
        ThreadChatO.stop(self)
        leave_channel(self.channel)


def leave_channel(channel):
    if channel in POKEMON.channel_list:
        POKEMON.remove_channel(channel)
        logger.info(
            f"Leaving Pokemon: {channel}", extra={"emoji": ":speech_balloon:"}
        )
        if len(POKEMON.channel_list) == 0:
            poke_logger.info("Nobody is streaming Pokemon CG")
            POKEMON.save_settings()

    if channel in POKEMON.online_channels:
        POKEMON.channel_offline(channel)

    if channel == THREADCONTROLLER.client_channel:
        logger.info(
            f"Disconnecting primary channel ({channel})", extra={"emoji": ":speech_balloon:"}
        )
        THREADCONTROLLER.client_channel = None
        THREADCONTROLLER.client = None


ChatPresence = ChatPresenceO
