from datetime import datetime, timedelta
from time import sleep
from dateutil.parser import parse
import random
import logging

from .ChatO import ClientIRC as ClientIRCO
from .ChatO import ChatPresence as ChatPresenceO
from .ChatO import ThreadChat as ThreadChatO
from .ChatO import logger

from .entities.Pokemon import PokemonComunityGame, CGApi
from .WinAlerts import send_alert
from .DiscordAPI import DiscordAPI

formatter = logging.Formatter('%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler("logs/pokemoncg.txt", encoding='utf-8')
file_handler.setFormatter(formatter)
poke_logger = logging.getLogger(__name__ + "pokemon")
poke_logger.setLevel(logging.DEBUG)
poke_logger.addHandler(file_handler)

POKEMON_CHECK_DELAY = 45  # seconds
POKEMON_CHECK_DELAY_RELAX = 60 * 14  # 14 mins
POKEMON_CHECK_LIMIT = 60  # pokemon is valid for 60 seconds

MARBLES_DELAY = 60 * 3  # seconds
MARBLES_TRIGGER_COUNT = 3

REDLOG = "\x1b[31;20m"
GREENLOG = "\x1b[32;20m"
YELLOWLOG = "\x1b[36;20m"

POKEMON = PokemonComunityGame()
POKEMON.set_delay(POKEMON_CHECK_DELAY)
DISCORD = DiscordAPI(POKEMON.discord.data["auth"])
DISCORD_CATCH_ALERTS = "https://discord.com/api/v9/channels/1072557550526013440/messages"


CHARACTERS = {
    "starter": "⭐",
    "female": "♀"
}


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

    def have_pokemon(self):
        return self.pokemon_active and self.pokemon_disabled is False

    def on_pubmsg(self, client, message):
        argstring = " ".join(message.arguments)

        if "pokemoncommunitygame" in message.source:
            self.check_pokemon_active(client, message, argstring)

        if self.have_pokemon():
            if POKEMON.check_catch():
                self.check_main(client)

    def check_pokemon_active(self, client, message, argstring):

        if "Spawns and payouts are disabled" in argstring:
            self.pokemon_disabled = True
            self.pokemon_active = False
            logger.info(f"Pokemon Disabled: {self.channel}", extra={"emoji": ":speech_balloon:"})
            leave_channel(self.channel[1:])
        elif self.pokemon_active is False and self.pokemon_disabled is False:
            self.pokemon_active = True
            self.log(f"{YELLOWLOG}Joined Pokemon for {message.target[1:]}")
            POKEMON.add_channel(message.target[1:])

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
                        hours = int(can_trade_in.split(" ")[0])
                    else:
                        hours = 0
                    if "minute" in can_trade_in:
                        minutes = int(can_trade_in.split(" ")[-2])
                    else:
                        minutes = 0

                    POKEMON.wondertrade_timer = datetime.utcnow() - timedelta(minutes=minutes, hours=hours)

            if POKEMON.check_wondertrade():
                POKEMON.reset_wondertrade_timer()
                pokemon_to_trade = None

                for tier in ["A", "B", "C"]:
                    if pokemon_to_trade is not None:
                        break
                    looking_for = f"trade{tier}"
                    for pokemon in allpokemon:
                        if pokemon["nickname"] is None:
                            continue
                        if looking_for in pokemon["nickname"]:
                            pokemon_to_trade = pokemon
                            break

                if pokemon_to_trade is None:
                    self.log(f"{REDLOG}Could not find a pokemon to wondertrade")
                else:
                    pokemon_received = self.pokemon_api.wondertrade(pokemon_to_trade["id"])
                    if "pokemon" in pokemon_received:
                        self.log(f"{GREENLOG}Wondertraded {pokemon_to_trade['name']} for {pokemon_received['pokemon']['name']}")
                    else:
                        self.log(f"{REDLOG}Wondertrade failed {pokemon_received}")

    def sort_computer(self):
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
                if index == 0:
                    if POKEMON.pokedex.starter(pokemon["name"]):
                        nick = CHARACTERS["starter"] + pokemon["name"]
                    elif POKEMON.pokedex.female(pokemon["pokedexId"]):
                        nick = pokemon["name"] + CHARACTERS["female"]
                    elif pokemon["nickname"] is None or pokemon["nickname"].startswith("trade") is False:
                        # if not starter and not female and has nickname, dont mess
                        continue
                    else:
                        nick = ""
                else:
                    nick = "trade" + POKEMON.pokedex.tier(pokemon["name"])
                    if POKEMON.pokedex.starter(pokemon["name"]):
                        nick = CHARACTERS["starter"] + nick
                    elif POKEMON.pokedex.female(pokemon["pokedexId"]):
                        nick = nick + CHARACTERS["female"]

                if pokemon["nickname"] == nick:
                    continue
                changes.append((pokemon["id"], nick, pokemon["name"], pokemon["nickname"]))

        for pokemon in shineys:
            if pokemon["nickname"] is not None:
                changes.append((pokemon["id"], "", pokemon["name"], pokemon["nickname"]))

        for poke_id, new_name, real_name, old_name in changes:
            self.pokemon_api.set_name(poke_id, new_name)
            self.log_file(f"{YELLOWLOG}Renamed {real_name} from {old_name} to {new_name}")
            sleep(0.5)

    def check_main(self, client):
        POKEMON.reset_timer()
        self.log_file(f"{GREENLOG}Checking pokemon spawn in pokeping")
        pokemon = POKEMON.get_last_spawned()

        if (datetime.utcnow() - pokemon.spawn).total_seconds() <= POKEMON_CHECK_LIMIT:
            # pokemon spawned recently relax and process it
            POKEMON.delay = POKEMON_CHECK_DELAY_RELAX
            self.log_file(f"{GREENLOG}Pokemon spawned - processing {pokemon}")

            dex = self.pokemon_api.get_pokedex()
            POKEMON.sync_pokedex(dex)

            all_pokemon = self.pokemon_api.get_all_pokemon()
            POKEMON.sync_computer(all_pokemon)

            catch_reasons, best_ball = POKEMON.need_pokemon(pokemon)
            repeat = True
            for reason in ["pokedex", "bag", "alt"]:
                if reason in catch_reasons:
                    repeat = False
                    break

            if len(catch_reasons) > 0:
                inv = self.pokemon_api.get_inventory()
                POKEMON.sync_inventory(inv)

                ball = POKEMON.inventory.get_catch_ball(pokemon.types, repeat=repeat, best=best_ball)
                random_channel = POKEMON.random_channel()
                message = f"!pokecatch {ball}"
                client.privmsg("#" + random_channel, message)

                reasons_string = ", ".join([POKEMON.missions.mission_message(reason) for reason in catch_reasons])
                self.log_file(f"{GREENLOG}Trying to catch {pokemon.name} with {ball} because {reasons_string}")

                sleep(5)

                all_pokemon = self.pokemon_api.get_all_pokemon()
                POKEMON.sync_computer(all_pokemon)

                # find all the pokemon that are the current one that spawned
                filtered = POKEMON.computer.get_pokemon(pokemon)
                caught = False
                for poke in filtered:
                    if (datetime.utcnow() - parse(poke["caughtAt"][:-1])).total_seconds() < 60:
                        caught = True
                        break

                discord_pokemon_name = pokemon.name if pokemon.is_alternate is False else pokemon.alt_name
                if caught:
                    self.log_file(f"{GREENLOG}Caught {pokemon.name}")
                    msg = f"I caught a {discord_pokemon_name}! =P"
                else:
                    self.log_file(f"{REDLOG}Failed to catch {pokemon.name}")
                    msg = f"I missed {discord_pokemon_name}! ='("

                DISCORD.post(DISCORD_CATCH_ALERTS, msg)
            else:
                self.log_file(f"{REDLOG}Don't need pokemon, skipping")
                random_channel = POKEMON.random_channel()
                client.privmsg("#" + random_channel, "!pokecheck")

            self.sort_computer()
            self.check_wondertrade()
        else:
            # pokemon should be spawning soon
            POKEMON.delay = POKEMON_CHECK_DELAY
            self.log_file(f"{YELLOWLOG}Pokemon spawning soon")

    def buy_shop(self, client, item, amount):
        # OLD - NEEDS REWORKING
        msg = "{color}Bought {amount} {item}{plural}".format(
            color=GREENLOG,
            amount=amount,
            item=item,
            plural="s" if amount > 0 else ""
        )

        if item.endswith("ball") and amount > 9:
            msg = msg + " and got {amount} bonus premierball{plural}".format(
                amount=amount // 10,
                plural="s" if amount // 10 > 1 else ""
            )

        # self.send_random_channel(client, "!pokeshop {item} {amount}".format(item=item, amount=amount), msg, logtofile=True, wait=15)


class ClientIRC(ClientIRCMarbles, ClientIRCPokemon):
    def __init__(self, username, token, channel, get_pokemoncg_token, marbles):
        ClientIRCMarbles.__init__(self, username, token, channel, marbles)
        ClientIRCPokemon.init(self, username, get_pokemoncg_token)

    def on_pubmsg(self, client, message):
        ClientIRCMarbles.on_pubmsg(self, client, message)
        ClientIRCPokemon.on_pubmsg(self, client, message)


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


ChatPresence = ChatPresenceO
