POKEPING_CHANNEL = "935704401954349196"
POKEMON_SPECIAL_ALTS = ["Minior", "Lycanroc", "Aegislash", "Rotom"]
POKEMON_WITH_ALTERNATE_VERSIONS = ["Abomasnow", "Aegislash", "Aipom", "Alcremie", "Ambipom", "Appletun", "Arcanine", "Basculegion", "Basculin", "Beautifly", "Bibarel", "Bidoof", "Blaziken", "Braviary", "Buizel", "Burmy", "Butterfree", "Cacturne", "Camerupt", "Castform", "Centiskorch", "Charizard", "Cherrim", "Coalossal", "Combee", "Croagunk", "Darmanitan", "Deerling", "Diglett", "Donphan", "Dugtrio", "Dustox", "Exeggutor", "Finneon", "Frillish", "Gabite", "Garchomp", "Geodude", "Gible", "Girafarig", "Gligar", "Golbat", "Golem", "Goodra", "Gourgeist", "Graveler", "Grimer", "Growlithe", "Gulpin", "Heracross", "Hippowdon", "Houndoom", "Indeedee", "Jellicent", "Kricketot", "Krikcetune", "Ledian", "Ledyba", "Lilligant", "Ludicolo", "Lumineon", "Luxio", "Luxray", "Lycanroc", "Magikarp", "Magnemite", "Mamoswine", "Marowak", "Meditite", "Meowstic", "Meowth", "Milotic", "Minior", "Morpeko", "Mr-Mime", "Muk", "Murkrow", "Ninetales", "Numel", "Nuzleaf", "Octillery", "Orbeetle", "Oricorio", "Overqwil", "Pachirisu", "Palossand", "Persian", "Pikachu", "Piloswine", "Politoed", "Polteageist", "Ponyta", "Pumpkaboo", "Pyroar", "Quagsire", "Raichu", "Rapidash", "Raticate", "Rattata", "Relicanth", "Rhydon", "Rhyperior", "Rockruff", "Roselia", "Roserade", "Rotom", "Sandaconda", "Sandshrew", "Sandslash", "Sawsbuck", "Scizor", "Scyther", "Shellos", "Shiftry", "Shinx", "Sinistea", "Slowbro", "Vivillon", "Voltorb", "Vulpix", "Weavile", "Weezing", "Wishiwashi", "Wobbuffet", "Wooper", "Wormadam", "Xatu", "Yamask", "Zigzagoon", "Zoroark", "Zorua", "Zubat"]

ROLES = {
    "bst": {
        "<@&960299429288620173>": 500,
    },
    "weight": {},
    "alter": "1068127190614552667"

}


class Pokemon(object):
    def __init__(self, dirty, clean):
        self.dirty_name = dirty
        self.name = clean

        self.bst = 0
        self.weight = 0

        self.is_alternate = False
        self.alt_id = "0"
        self.alt_name = "NA"

    def __str__(self):
        alter = str(self.is_alternate)
        to_ret = f"{self.dirty_name} (clean: {self.name}), bst={self.bst}, weight={self.weight}KG, alter={alter}"
        if self.is_alternate:
            to_ret = f"{to_ret} (id: {self.alt_id}, name: {self.alt_name})"
        return to_ret

    def parse(self, data):
        print(ROLES)
        print(ROLES["alter"])
        print(data)
        print(data["mention_roles"])
        if ROLES["alter"] in data["mention_roles"]:
            # must parse alt message
            self.is_alternate = True
            self.alt_id = data["content"].split("ID: ")[1].split(" ")[0]
            self.alt_name = data["content"].split("| ")[2].split(" ")[0]
        else:
            # is normal pokemon message
            temp = data["content"].split(" KG ")[0].split(" - ")

            w = temp[-1]
            if w in ROLES["weight"]:
                w = ROLES["weight"][w]
            self.weight = float(w)

            b = temp[-2].split(" ")[-1]
            if b in ROLES["bst"]:
                b = ROLES["bst"][b]
            self.bst = int(b)

    def check_special_cases(self):
        if self.name in POKEMON_SPECIAL_ALTS:
            self.is_alternate = True
            self.alt_name = self.dirty_name
            self.id = self.dirty_name


class Pokeping(object):
    def __init__(self):
        self.discord = None

    def set_discord(self, discord):
        self.discord = discord

    def scan(self, dirty):
        clean = self.clean_name(dirty)

        pokemon = Pokemon(dirty, clean)
        pokemon.parse(self.get_last_message())

        if pokemon.is_alternate:
            pokemon.parse(self.get_last_message(2))
        else:
            pokemon.check_special_cases()

        return pokemon

    def get_last_message(self, limit=1):
        url = f"https://discord.com/api/v9/channels/{POKEPING_CHANNEL}/messages?limit={limit}"
        data = self.discord.get(url)
        data = data[-1]
        return data
