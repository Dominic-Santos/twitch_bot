from datetime import datetime
from time import sleep
import logging

from .ChatO import ClientIRC as ClientIRCO
from .ChatO import ChatPresence as ChatPresenceO
from .ChatO import ThreadChat as ThreadChatO
from .ChatO import logger

from .entities.Pokemon import PokemonComunityGame

MARBLES_DELAY = 60 * 3  # seconds
MARBLES_TRIGGER_COUNT = 3

POKEMON = PokemonComunityGame()

REDLOG = "\x1b[31;20m"
GREENLOG = "\x1b[32;20m"
YELLOWLOG = "\x1b[36;20m"


formatter = logging.Formatter('%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler("logs/pokemoncg.txt")
file_handler.setFormatter(formatter)
poke_logger = logging.getLogger(__name__ + "pokemon")
poke_logger.setLevel(logging.DEBUG)
poke_logger.addHandler(file_handler)


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
        self.marbles_timer = datetime.now()
        self.marbles_counter = 0

    def on_pubmsg(self, client, message):
        if self.marbles and "!play" in " ".join(message.arguments):
            self.check_marbles(client, message)

    def check_marbles(self, client, message):
        now = datetime.now()
        if (now - self.marbles_timer).total_seconds() > MARBLES_DELAY:
            self.marbles_timer = now
            self.marbles_counter = 0

        self.marbles_counter += 1

        if self.marbles_counter == MARBLES_TRIGGER_COUNT:
            client.privmsg(message.target, "!play")
            self.log(f"Joined Marbles for {message.target[1:]}")


class ClientIRCPokemon(ClientIRCBase):
    def __init__(self, username, token, channel):
        ClientIRCBase.__init__(self, username, token, channel)
        self.init(username)

    def init(self, username):
        self.username = username.lower()
        self.at_username = "@" + self.username

        self.pokemon_active = False

    @staticmethod
    def log_file(msg):
        poke_logger.info(msg)

    def on_pubmsg(self, client, message):
        argstring = " ".join(message.arguments)

        if "!pokecatch" in argstring:
            self.check_pokemon(client)

        if argstring.startswith(self.at_username):
            if "registered in Pokédex" in argstring:
                self.check_should_catch(client, argstring)
            elif "Balance" in argstring:
                self.update_balance(client, argstring)

        if "pokemoncommunitygame" in message.source:
            self.check_pokemon_active(client, message)
            self.check_pokemon_caught(client, message, argstring)

    def update_balance(self, client, argstring):
        try:
            cash = int(argstring.split("$")[1].split(" ")[0])
        except:
            self.log(f"{REDLOG}Failed to parse current balance: {argstring}")
            cash = 0
        else:
            POKEMON.set_cash(cash)
            buy_list = POKEMON.get_purchase_list(True)

            for item, amount in buy_list:
                self.buy_shop(client, item, amount)

            self.log_file(f"{YELLOWLOG}" + POKEMON.get_inventory())
            POKEMON.save_settings()

    def buy_shop(self, client, item, amount):
        msg = "{color}Bought {amount} {item}{plural}".format(
            color=GREENLOG,
            amount=amount,
            item=item,
            plural="s" if amount > 0 else ""
        )

        premierballs = 0
        if item.endswith("ball") and amount > 9:
            premierballs = amount // 10
            msg = msg + " and got {amount} bonus premierball{plural}".format(
                amount=amount // 10,
                plural="s" if amount // 10 > 1 else ""
            )

        self.send_random_channel(client, "!pokeshop {item} {amount}".format(item=item, amount=amount), msg, logtofile=True)

        POKEMON.add_item(item, amount)
        if premierballs > 0:
            POKEMON.add_item("premierball", premierballs)

    def check_pokemon_active(self, client, message):
        if self.pokemon_active is False:
            self.pokemon_active = True
            self.log(f"{YELLOWLOG}Joined Pokemon for {message.target[1:]}")
            POKEMON.add_channel(message.target[1:])

    def check_pokemon(self, client):
        if POKEMON.check_catch():
            self.send_random_channel(client, "!pokecheck", "Checking if need current Pokemon in {channel} stream")

    def catch_pokemon(self, client, pokemon):
        random_channel = self.send_random_channel(client, POKEMON.get_catch_message(), GREENLOG + "Trying to catch " + pokemon + " in {channel} stream")
        POKEMON.last_attempt(pokemon, random_channel)

    def check_pokemon_caught(self, client, message, argstring):
        last_catch, last_channel = POKEMON.last_attempt()
        if message.target[1:] == last_channel:
            if argstring.startswith(last_catch + " has been caught by:"):
                if self.username in argstring:
                    self.log_file(f"{GREENLOG}Caught {last_catch}")
                    POKEMON.check_type_mission(inc=True)
                elif argstring.endswith("..."):
                    self.log_file(f"{YELLOWLOG}I don't know if {last_catch} was caught, too many users")
                else:
                    self.log_file(f"{REDLOG}Failed to catch {last_catch}")
            elif argstring.startswith(last_catch + " escaped."):
                self.log_file(f"{REDLOG}Failed to catch {last_catch}")

    def get_pokemon(self, argstring):
        args = argstring.split(" ")
        pokemon = args[1]
        if pokemon.startswith("Nidoran"):
            pokemon = "Nidoran-{sex}".format(sex="male" if pokemon.endswith("♂") else "female")
        elif pokemon == "Mime":
            pokemon = "Mime-jr"
        elif pokemon.startswith("Mr"):
            pokemon = "Mr-{poke}".format(poke=args[2])
        return pokemon

    def check_should_catch(self, client, argstring):
        last_catch, last_channel = POKEMON.last_attempt()
        pokemon = self.get_pokemon(argstring)

        if last_catch == pokemon:
            self.log(f"{YELLOWLOG}Already decided on {pokemon}")
        else:
            POKEMON.get_pokemon_type(pokemon)
            if argstring.endswith("❌"):
                self.catch_pokemon(client, pokemon)
            elif POKEMON.check_type_mission():
                mission = POKEMON.settings["type_mission"]
                self.log_file(f"{GREENLOG}Already have {pokemon} but is {mission} type")
                self.catch_pokemon(client, pokemon)
            else:
                self.log_file(f"{REDLOG}Won't catch {pokemon}")
                POKEMON.last_attempt(pokemon, None)
            self.check_balance(client)

    def check_balance(self, client):
        if POKEMON.check_balance():
            self.send_random_channel(client, "!pokepass", YELLOWLOG + "Checking balance in {channel}")

    def send_random_channel(self, client, message, logmessage=None, logtofile=False):
        random_channel = POKEMON.random_channel()
        if random_channel is not None:
            client.privmsg("#" + random_channel, message)
            if logmessage is not None:
                if logtofile:
                    self.log_file(logmessage.format(channel=random_channel))
                else:
                    self.log(logmessage.format(channel=random_channel))
        return random_channel


class ClientIRC(ClientIRCMarbles, ClientIRCPokemon):
    def __init__(self, username, token, channel, marbles):
        ClientIRCMarbles.__init__(self, username, token, channel, marbles)
        ClientIRCPokemon.init(self, username)

    def on_pubmsg(self, client, message):
        ClientIRCMarbles.on_pubmsg(self, client, message)
        ClientIRCPokemon.on_pubmsg(self, client, message)


class ThreadChat(ThreadChatO):
    def __init__(self, username, token, channel, marbles):
        ThreadChatO.__init__(self, username, token, channel)
        self.marbles = marbles

    def run(self):
        self.chat_irc = ClientIRC(self.username, self.token, self.channel, self.marbles)
        logger.info(
            f"Join IRC Chat: {self.channel}", extra={"emoji": ":speech_balloon:"}
        )
        self.chat_irc.start()

    def stop(self):
        ThreadChatO.stop(self)
        if self.channel in POKEMON.channel_list:
            POKEMON.remove_channel(self.channel)
            logger.info(
                f"Leaving Pokemon: {self.channel}", extra={"emoji": ":speech_balloon:"}
            )


ChatPresence = ChatPresenceO
