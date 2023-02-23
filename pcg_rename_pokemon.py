from TwitchChannelPointsMinerLocal.classes.entities.Pokemon import CGApi, Pokedex
from time import sleep
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Referer": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv/",
    "Origin": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv",
    "Accept": "application/json, text/plain, */*",
    "Authorization": "token here"
}

URL = "https://poketwitch.bframework.de/api/game/ext/trainer/pokemon/"

characters = {
    "starter": "⭐",
    "female": "♀"
}

female_pokemon = [10025, 86320, 10143, 10144, 10262, 10284, 10285, 10286, 10287, 10288, 10292, 10295, 10302, 10309, 10316, 10319, 10325, 10340, 10350, 10352, 10359, 10360, 10361, 10362, 10365, 10368, 10370, 10372, 10373, 10375, 10378, 10379, 10381, 10382, 10384, 10385, 10387, 10388, 10391, 10392, 10396, 10404, 10418, 10422, 10423, 10424, 10427, 10429, 10438, 10441, 10442, 10445, 10446, 10449, 10451, 10452, 10453, 10454, 10455, 10456, 10467, 10468, 10470, 10471, 10540, 10543, 10544, 10545, 10553]


def main():
    api = CGApi(HEADERS["Authorization"])
    allpokemon = api.get_all_pokemon()
    pokedex = Pokedex()

    pokedict = {}
    shineys = []
    for pokemon in allpokemon["allPokemon"]:
        if pokemon["isShiny"]:
            shineys.append(pokemon)
        else:
            pokedict.setdefault(pokemon["pokedexId"], []).append(pokemon)

    changes = []
    for pokeid in pokedict.keys():
        ordered = sorted(pokedict[pokeid], key=lambda x: (-x["avgIV"], -x["lvl"]))
        for index, pokemon in enumerate(ordered):
            clean_name = pokedex.clean_name(pokemon["name"])
            if index == 0:
                if pokedex.starter(clean_name):
                    nick = characters["starter"] + pokemon["name"]
                elif pokemon["pokedexId"] in female_pokemon:
                    nick = pokemon["name"] + characters["female"]
                elif pokemon["nickname"] is None or pokemon["nickname"].startswith("trade") is False:
                    # if not starter and not female and has nickname, dont mess
                    continue
                else:
                    nick = ""
            else:
                nick = "trade" + pokedex.tier(clean_name)
                if pokedex.starter(clean_name):
                    nick = characters["starter"] + nick
                elif pokemon["pokedexId"] in female_pokemon:
                    nick = nick + characters["female"]

            if pokemon["nickname"] == nick:
                continue
            changes.append((pokemon["id"], nick, pokemon["name"], pokemon["nickname"]))

    for pokemon in shineys:
        if pokemon["nickname"] is not None:
            changes.append((pokemon["id"], "", pokemon["name"], pokemon["nickname"]))

    for poke_id, new_name, real_name, old_name in changes:
        api.set_name(poke_id, new_name)
        print(f"renamed {real_name} from {old_name} to {new_name}")
        sleep(0.5)


if __name__ == "__main__":
    main()
