import json
from time import sleep
from datetime import datetime

from TwitchChannelPointsMinerLocal.classes.entities.Pokemon.Discord import Discord
from TwitchChannelPointsMinerLocal.classes.entities.Pokemon.Pokedex import Pokedex
from TwitchChannelPointsMinerLocal.classes.entities.Pokemon.Pokeping import Pokeping


SETTINGS_FILE = "pokemon.json"
ALERTS_CHANNEL = 860191353483558993
DISCORD_BASE = "https://discord.com/api/v9/"
DISCORD_ALERTS = f"{DISCORD_BASE}channels/{ALERTS_CHANNEL}/messages"
MARZ = 689450584528781355

NEEDS = [
    "Gloom", "Poliwrath", "Aerodactyl", "Dragonite", "Espeon", "Loudred", "Vespiquen",
    "Mismagius", "Honchkrow", "Garchomp", "Drapion", "Toxicroak", "Weavile", "Excadrill",
    "Leavanny", "Florges", "Tyrantrum", "Mimikyu", "Copperajah"
]


def load_json(the_file):
    with open(the_file, "r") as f:
        j = json.load(f)
        return j


def main():
    settings = load_json(SETTINGS_FILE)
    dex = load_json("results/API/get_pokedex.json")
    discord = Discord()
    discord.set(settings["discord"])
    discord.connect()

    pokeping = Pokeping()
    pokeping.set_discord(discord)
    pokeping.get_roles()

    pokedex = Pokedex()
    pokedex.set(dex)
    for pokemon_name in pokedex.pokemon:
        pokedex.pokemon[pokemon_name] = pokemon_name not in NEEDS

    old_pokemon = pokeping.get_pokemon()

    while True:
        sleep(30)
        now = datetime.now()
        pokemon = pokeping.get_pokemon()

        if pokemon.spawn == old_pokemon.spawn:
            print(now, "- same pokemon, skipping", pokemon)
            continue

        if pokedex.need(pokemon):
            print(now, "- need, sending alert to marz", pokemon)
            discord.post(DISCORD_ALERTS, "Quick <@{u}> a pokemon spawned {pokemon}".format(u=MARZ, pokemon=pokemon))
        else:
            print(now, "- marz doesn't need", pokemon)

        old_pokemon = pokemon

        sleep(13.5 * 60)


if __name__ == "__main__":
    main()
