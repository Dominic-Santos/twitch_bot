import random
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

POKEMON_INFO_URL = "https://www.pokemon.com/us/pokedex/{pokemon}"
POKEPING_CHANNEL = "935704401954349196"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

CATCH_TRIGGER = 10
CATCH_DELAY = 60  # seconds
CATCH_BALL_PRIORITY = ["ultraball", "greatball", "premierball", "pokeball"]
CATCH_SPECIAL_BALLS = {
    "Water": "netball",
    "Bug": "netball",
    "Dark": "nightball",
    "Ghost": "phantomball",
    "Poison": "cipherball",
    "Psychic": "cipherball",
    "Ice": "frozenball"
}

SETTINGS_FILE = "pokemon.json"
POKEDEX_FILE = "pokedex.json"

BALANCE_TRIGGER = 1
ITEM_MIN_AMOUNT = 30
ITEM_MIN_PURCHASE = 10
ITEM_PRIORITY = ["pokeball", "ultraball"]
ITEM_PRICES = {
    "pokeball": 300,
    "greatball": 600,
    "ultraball": 1000,
}

POKEMON_WITH_ALTERNATE_VERSIONS = ["Abomasnow", "Aegislash", "Aegislash (Blade)", "Aegislash (Shield)", "Aipom", "Alcremie", "Ambipom", "Appletun", "Arcanine", "Basculegion", "Basculin", "Beautifly", "Bibarel", "Bidoof", "Blaziken", "Braviary", "Buizel", "Burmy", "Butterfree", "Cacturne", "Camerupt", "Castform", "Centiskorch", "Charizard", "Cherrim", "Coalossal", "Combee", "Croagunk", "Darmanitan", "Deerling", "Diglett", "Donphan", "Dugtrio", "Dustox", "Exeggutor", "Finneon", "Frillish", "Gabite", "Garchomp", "Geodude", "Gible", "Girafarig", "Gligar", "Golbat", "Golem", "Goodra", "Gourgeist", "Graveler", "Grimer", "Growlithe", "Gulpin", "Heracross", "Hippowdon", "Houndoom", "Indeedee", "Jellicent", "Kricketot", "Krikcetune", "Ledian", "Ledyba", "Lilligant", "Ludicolo", "Lumineon", "Luxio", "Luxray", "Lycanroc", "Magikarp", "Magnemite", "Mamoswine", "Marowak", "Meditite", "Meowstic", "Meowth", "Milotic", "Minior", "Morpeko", "Mr-Mime", "Muk", "Murkrow", "Ninetales", "Numel", "Nuzleaf", "Octillery", "Orbeetle", "Oricorio", "Overqwil", "Pachirisu", "Palossand", "Persian", "Pikachu", "Piloswine", "Politoed", "Polteageist", "Ponyta", "Pumpkaboo", "Pyroar", "Quagsire", "Raichu", "Rapidash", "Raticate", "Rattata", "Relicanth", "Rhydon", "Rhyperior", "Rockruff", "Roselia", "Roserade", "Rotom", "Sandaconda", "Sandshrew", "Sandslash", "Sawsbuck", "Scizor", "Scyther", "Shellos", "Shiftry", "Shinx", "Sinistea", "Slowbro", "Vivillon", "Voltorb", "Vulpix", "Weavile", "Weezing", "Wishiwashi", "Wobbuffet", "Wooper", "Wormadam", "Xatu", "Yamask", "Zigzagoon", "Zoroark", "Zorua", "Zubat"]
POKEMON_TIERS = {
    "S": ["Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune", "Lugia", "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect", "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion", "Type:Null", "Silvally", "TapuKoko", "TapuLele", "TapuBulu", "TapuFini", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", "Kartana", "Guzzlord", "Necrozma", "Magearna", "Marshadow", "Poipole", "Naganadel", "Stakataka", "Blacephalon", "Zeraora", "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex", "Ting-lu", "Chien-pao", "Wo-chien", "Chi-yu", "Koraidon", "Miraidon"],
    "A": ["Raichu", "Nidoqueen", "Nidoking", "Vileplume", "Arcanine", "Poliwrath", "Alakazam", "Machamp", "Victreebel", "Golem", "Gengar", "Starmie", "Gyarados", "Lapras", "Vaporeon", "Jolteon", "Flareon", "Aerodactyl", "Snorlax", "Dragonite", "Crobat", "Politoed", "Espeon", "Umbreon", "Slowking", "Steelix", "Scizor", "Kingdra", "Blissey", "Pupitar", "Tyranitar", "Ludicolo", "Shiftry", "Gardevoir", "Slaking", "Aggron", "Wailord", "Camerupt", "Flygon", "Altaria", "Milotic", "Walrein", "Salamence", "Metagross", "Luxray", "Roserade", "Rampardos", "Bastiodon", "Vespiquen", "Drifblim", "Mismagius", "Honchkrow", "Spiritomb", "Garchomp", "Lucario", "Hippowdon", "Toxicroak", "Abomasnow", "Weavile", "Magnezone", "Lickilicky", "Rhyperior", "Electivire", "Magmortar", "Togekiss", "Yanmega", "Leafeon", "Glaceon", "Gliscor", "Mamoswine", "Porygon-Z", "Gallade", "Dusknoir", "Froslass", "Rotom", "Gigalith", "Excadrill", "Conkeldurr", "Seismitoad", "Leavanny", "Scolipede", "Krookodile", "Darmanitan", "Cofagrigus", "Archeops", "Zoroark", "Gothitelle", "Reuniclus", "Vanilluxe", "Ferrothorn", "Klinklang", "Eelektross", "Chandelure", "Haxorus", "Druddigon", "Golurk", "Bisharp", "Hydreigon", "Volcarona", "Talonflame", "Pyroar", "Florges", "Pangoro", "Aegislash", "Dragalge", "Tyrantrum", "Sylveon", "Hawlucha", "Goodra", "Noivern", "Toucannon", "Vikavolt", "Toxapex", "Salazzle", "Bewear", "Tsareena", "Golisopod", "Turtonator", "Mimikyu", "Kommo-o", "Corviknight", "Orbeetle", "Coalossal", "Flapple", "Appletun", "Toxtricity", "Centiskorch", "Polteageist", "Hatterene", "Grimmsnarl", "Obstagoon", "Cursola", "Mr-Rime", "Runerigus", "Alcremie", "Copperajah", "Duraludon", "Drakloak", "Dragapult", "Farigiraf", "Dondozo", "Arboliva", "Revavroom", "Cetitan", "Baxcalibur", "Cyclizar", "Pawmot", "Flamigo", "Garganacl", "Glimmora", "Mabosstiff", "Gholdengo", "GreatTusk", "BruteBonnet", "SandyShocks", "ScreamTail", "FlutterMane", "SlitherWing", "RoaringMoon", "IronTreads", "IronMoth", "IronHands", "IronJugulis", "IronThorns", "IronBundle", "IronValiant", "Tinkaton", "Armarouge", "Ceruledge", "Kingambit", "Annihilape"],
    "B": ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Butterfree", "Beedrill", "Pidgeotto", "Pidgeot", "Raticate", "Fearow", "Arbok", "Pikachu", "Sandslash", "Nidorina", "Nidorino", "Clefable", "Ninetales", "Wigglytuff", "Gloom", "Parasect", "Venomoth", "Dugtrio", "Persian", "Golduck", "Primeape", "Poliwhirl", "Kadabra", "Machoke", "Weepinbell", "Tentacruel", "Graveler", "Rapidash", "Slowbro", "Magneton", "Dodrio", "Dewgong", "Muk", "Cloyster", "Haunter", "Hypno", "Kingler", "Electrode", "Exeggutor", "Marowak", "Hitmonlee", "Hitmonchan", "Weezing", "Rhydon", "Seadra", "Seaking", "Scyther", "Electabuzz", "Magmar", "Pinsir", "Eevee", "Porygon", "Omastar", "Kabutops", "Dratini", "Dragonair", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Furret", "Noctowl", "Ledian", "Ariados", "Lanturn", "Pichu", "Togetic", "Xatu", "Flaaffy", "Ampharos", "Bellossom", "Azumarill", "Skiploom", "Jumpluff", "Sunflora", "Quagsire", "Wobbuffet", "Forretress", "Granbull", "Heracross", "Ursaring", "Magcargo", "Piloswine", "Octillery", "Skarmory", "Houndoom", "Donphan", "Porygon2", "Hitmontop", "Larvitar", "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", "Swampert", "Mightyena", "Linoone", "Beautifly", "Dustox", "Lombre", "Nuzleaf", "Swellow", "Pelipper", "Kirlia", "Masquerain", "Breloom", "Vigoroth", "Shedinja", "Loudred", "Exploud", "Hariyama", "Delcatty", "Lairon", "Medicham", "Manectric", "Swalot", "Sharpedo", "Torkoal", "Grumpig", "Trapinch", "Vibrava", "Cacturne", "Zangoose", "Seviper", "Whiscash", "Crawdaunt", "Claydol", "Cradily", "Armaldo", "Feebas", "Castform", "Kecleon", "Banette", "Dusclops", "Tropius", "Chimecho", "Absol", "Glalie", "Sealeo", "Huntail", "Gorebyss", "Relicanth", "Bagon", "Shelgon", "Beldum", "Metang", "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", "Empoleon", "Staravia", "Staraptor", "Bibarel", "Kricketune", "Luxio", "Wormadam", "Mothim", "Pachirisu", "Floatzel", "Cherrim", "Gastrodon", "Ambipom", "Lopunny", "Purugly", "Skuntank", "Bronzong", "Gible", "Gabite", "Riolu", "Drapion", "Carnivine", "Lumineon", "Tangrowth", "Probopass", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", "Oshawott", "Dewott", "Samurott", "Watchog", "Herdier", "Stoutland", "Liepard", "Simisage", "Simisear", "Simipour", "Musharna", "Tranquill", "Unfezant", "Zebstrika", "Boldore", "Swoobat", "Audino", "Gurdurr", "Palpitoad", "Throh", "Sawk", "Swadloon", "Whirlipede", "Whimsicott", "Lilligant", "Krokorok", "Crustle", "Scrafty", "Sigilyph", "Yamask", "Carracosta", "Garbodor", "Zorua", "Cinccino", "Gothorita", "Duosion", "Swanna", "Vanillish", "Sawsbuck", "Emolga", "Escavalier", "Amoonguss", "Jellicent", "Alomomola", "Galvantula", "Klang", "Eelektrik", "Beheeyem", "Lampent", "Axew", "Fraxure", "Beartic", "Cryogonal", "Accelgor", "Mienshao", "Bouffalant", "Braviary", "Mandibuzz", "Heatmor", "Durant", "Deino", "Zweilous", "Larvesta", "Chespin", "Quilladin", "Chesnaught", "Fennekin", "Braixen", "Delphox", "Froakie", "Frogadier", "Greninja", "Diggersby", "Fletchinder", "Spewpa", "Vivillon", "Floette", "Gogoat", "Meowstic", "Honedge", "Doublade", "Aromatisse", "Slurpuff", "Malamar", "Clawitzer", "Heliolisk", "Aurorus", "Dedenne", "Carbink", "Sliggoo", "Trevenant", "Gourgeist", "Avalugg", "Rowlet", "Dartrix", "Decidueye", "Litten", "Torracat", "Incineroar", "Popplio", "Brionne", "Primarina", "Trumbeak", "Gumshoos", "Charjabug", "Crabominable", "Ribombee", "Lycanroc", "Mudsdale", "Araquanid", "Lurantis", "Shiinotic", "Steenee", "Oranguru", "Passimian", "Palossand", "Minior", "Bruxish", "Drampa", "Dhelmise", "Jangmo-o", "Hakamo-o", "Grookey", "Thwackey", "Rillaboom", "Scorbunny", "Raboot", "Cinderace", "Sobble", "Drizzile", "Inteleon", "Dottler", "Thievul", "Eldegoss", "Dubwool", "Drednaw", "Boltund", "Carkol", "Applin", "Sandaconda", "Barraskewda", "Grapploct", "Hattrem", "Morgrem", "Sirfetch’d", "Frosmoth", "Stonjourner", "Eiscue", "Indeedee", "Morpeko", "Dracozolt", "Arctozolt", "Dracovish", "Arctovish", "Dreepy", "Sprigatito", "Floragato", "Meowscarada", "Fuecoco", "Crocalor", "Skeledirge", "Quaxly", "Quaxwell", "Quaquaval", "Oinkologne", "Dudunsparce", "Spidops", "Lokix", "Rabsca", "Houndstone", "Espathra", "Wugtrio", "Veluza", "Palafin", "Dolliv", "Scovillain", "Bellibolt", "Orthworm", "Maushold", "Arctibax", "Tatsugiri", "Pawmo", "Kilowattrel", "Bombirdier", "Klawf", "Naclstack", "Grafaiai", "Dachsbun", "Brambleghast", "Tinkatuff", "Toedscruel", "Clodsire"],
    "C": ["Caterpie", "Metapod", "Weedle", "Kakuna", "Pidgey", "Rattata", "Spearow", "Ekans", "Sandshrew", "Nidoran-female", "Nidoran-male", "Clefairy", "Vulpix", "Jigglypuff", "Zubat", "Golbat", "Oddish", "Paras", "Venonat", "Diglett", "Meowth", "Psyduck", "Mankey", "Growlithe", "Poliwag", "Abra", "Machop", "Bellsprout", "Tentacool", "Geodude", "Ponyta", "Slowpoke", "Magnemite", "Farfetch’d", "Doduo", "Seel", "Grimer", "Shellder", "Gastly", "Onix", "Drowzee", "Krabby", "Voltorb", "Exeggcute", "Cubone", "Lickitung", "Koffing", "Rhyhorn", "Chansey", "Tangela", "Kangaskhan", "Horsea", "Goldeen", "Staryu", "Mr.Mime", "Jynx", "Tauros", "Magikarp", "Ditto", "Omanyte", "Kabuto", "Sentret", "Hoothoot", "Ledyba", "Spinarak", "Chinchou", "Cleffa", "Igglybuff", "Togepi", "Natu", "Mareep", "Marill", "Sudowoodo", "Hoppip", "Aipom", "Sunkern", "Yanma", "Wooper", "Murkrow", "Misdreavus", "Unown", "Girafarig", "Pineco", "Dunsparce", "Gligar", "Snubbull", "Qwilfish", "Shuckle", "Sneasel", "Teddiursa", "Slugma", "Swinub", "Corsola", "Remoraid", "Delibird", "Mantine", "Houndour", "Phanpy", "Stantler", "Smeargle", "Tyrogue", "Smoochum", "Elekid", "Magby", "Miltank", "Poochyena", "Zigzagoon", "Wurmple", "Silcoon", "Cascoon", "Lotad", "Seedot", "Taillow", "Wingull", "Ralts", "Surskit", "Shroomish", "Slakoth", "Nincada", "Ninjask", "Whismur", "Makuhita", "Azurill", "Nosepass", "Skitty", "Sableye", "Mawile", "Aron", "Meditite", "Electrike", "Plusle", "Minun", "Volbeat", "Illumise", "Roselia", "Gulpin", "Carvanha", "Wailmer", "Numel", "Spoink", "Spinda", "Cacnea", "Swablu", "Lunatone", "Solrock", "Barboach", "Corphish", "Baltoy", "Lileep", "Anorith", "Shuppet", "Duskull", "Wynaut", "Snorunt", "Spheal", "Clamperl", "Luvdisc", "Starly", "Bidoof", "Kricketot", "Shinx", "Budew", "Cranidos", "Shieldon", "Burmy", "Combee", "Buizel", "Cherubi", "Shellos", "Drifloon", "Buneary", "Glameow", "Chingling", "Stunky", "Bronzor", "Bonsly", "MimeJr.", "Happiny", "Chatot", "Munchlax", "Hippopotas", "Skorupi", "Croagunk", "Finneon", "Mantyke", "Snover", "Patrat", "Lillipup", "Purrloin", "Pansage", "Pansear", "Panpour", "Munna", "Pidove", "Blitzle", "Roggenrola", "Woobat", "Drilbur", "Timburr", "Tympole", "Sewaddle", "Venipede", "Cottonee", "Petilil", "Basculin", "Sandile", "Darumaka", "Maractus", "Dwebble", "Scraggy", "Tirtouga", "Archen", "Trubbish", "Minccino", "Gothita", "Solosis", "Ducklett", "Vanillite", "Deerling", "Karrablast", "Foongus", "Frillish", "Joltik", "Ferroseed", "Klink", "Tynamo", "Elgyem", "Litwick", "Cubchoo", "Shelmet", "Stunfisk", "Mienfoo", "Golett", "Pawniard", "Rufflet", "Vullaby", "Bunnelby", "Fletchling", "Scatterbug", "Litleo", "Flabebe", "Skiddo", "Pancham", "Furfrou", "Espurr", "Spritzee", "Swirlix", "Inkay", "Binacle", "Barbaracle ", "Skrelp", "Clauncher", "Helioptile", "Tyrunt", "Amaura", "Goomy", "Klefki", "Phantump", "Pumpkaboo", "Bergmite", "Noibat", "Pikipek", "Yungoos", "Grubbin", "Crabrawler", "Oricorio", "Cutiefly", "Rockruff", "Wishiwashi", "Mareanie", "Mudbray", "Dewpider", "Fomantis", "Morelull", "Salandit", "Stufful", "Bounsweet", "Comfey", "Wimpod", "Sandygast", "Pyukumuku", "Komala", "Togedemaru", "Skwovet", "Greedent", "Rookidee", "Corvisquire", "Blipbug", "Nickit", "Gossifleur", "Wooloo", "Chewtle", "Yamper", "Rolycoly", "Silicobra", "Cramorant", "Arrokuda", "Toxel", "Sizzlipede", "Clobbopus", "Sinistea", "Hatenna", "Impidimp", "Perrserker", "Milcery", "Falinks", "Pincurchin", "Snom", "Cufant", "Lechonk", "Tarountula", "Nymble", "Rellor", "Greavard", "Flittle", "Wiglett", "Finizen", "Smoliv", "Capsakid", "Tadbulb", "Varoom", "Tandemaus", "Cetoddle", "Frigibax", "Pawmi", "Wattrel", "Squawkabilly", "Nacli", "Glimmet", "Shroodle", "Fidough", "Maschiff", "Bramblin", "Gimmighoul", "Tinkatink", "Charcadet", "Toedscool"]
}


class Pokedex(object):
    def __init__(self, discord=None):
        self.types = {}
        self.discord = discord
        self.load()

    def get(self, pokemon):
        return self.types.get(pokemon, [])

    def get_data(self, pokemon):
        res = requests.get(POKEMON_INFO_URL.format(pokemon=pokemon), headers=HEADERS)
        soup = BeautifulSoup(res.content, "html.parser")
        return soup

    def get_type_request(self, pokemon):
        try:
            data = self.get_data(pokemon)
            typedata = data.find("div", class_="dtm-type").find_all("a")
            types = [t.text for t in typedata]
            self.types[pokemon] = types
            self.save()
        except:
            pass

    def get_type(self, pokemon):
        if pokemon in self.types:
            return self.types[pokemon]

        self.get_type_request(pokemon)

        return self.get(pokemon)

    def save(self):
        with open(POKEDEX_FILE, "w") as f:
            f.write(json.dumps(self.types, indent=4))

    def load(self):
        try:
            with open(POKEDEX_FILE, "r") as f:
                self.types = json.load(f)
        except:
            self.types = {}

    @staticmethod
    def clean_name(pokemon):
        end = pokemon
        if pokemon.startswith("Nidoran"):
            end = "Nidoran-{sex}".format(sex="male" if pokemon.endswith("♂") else "female")
        elif pokemon == "Mime":
            end = "Mime-jr"
        elif pokemon.startswith("Mr"):
            end = "Mr-{poke}".format(poke=pokemon.split(" ")[1])
        end = end.replace("’", "")
        return end

    def alternate(self, pokemon):
        has_alts = pokemon in POKEMON_WITH_ALTERNATE_VERSIONS

        if self.discord is None:
            return has_alts

        if has_alts is False:
            return False

        url = f"https://discord.com/api/v9/channels/{POKEPING_CHANNEL}/messages?limit=1"
        headers = {"Authorization": self.discord["auth"]}

        r = requests.get(url, headers=headers)
        data = r.json()[0]
        return self.discord["roles"]["alter"] in data["mention_roles"]

    @staticmethod
    def tier(pokemon):
        for k in POKEMON_TIERS.keys():
            if pokemon in POKEMON_TIERS[k]:
                return k
        return None


class Inventory(object):
    def __init__(self):
        self.reset()
        self.last_used = None

    def __str__(self):
        return "Balance: $" + str(self.cash) + " " + ", ".join(["{item}: {amount}".format(item=item, amount=self.get_item(item)) for item in sorted(self.items.keys())])

    def get(self):
        return self.items

    def set(self, items):
        self.items = items

    def reset(self):
        self.items = {}
        self.cash = 0

    def add_item(self, item, amount):
        self.items[item] = self.get_item(item) + amount

    def remove_item(self, item, amount):
        self.items[item] = self.get_item(item) - amount

    def get_item(self, item):
        return self.items.get(item, 0)

    def set_item(self, item, amount):
        self.items[item] = amount

    def have_item(self, item):
        return self.get_item(item) > 0

    def use(self, item):
        if self.have_item(item):
            self.remove_item(item, 1)
            self.last_used = item

    def set_cash(self, cash):
        self.cash = cash

    def get_catch_ball(self, types=[], repeat=False):
        if repeat:
            if self.have_item("repeatball"):
                return "repeatball"

        if types is not None:
            for t in sorted(types):
                if t in CATCH_SPECIAL_BALLS:
                    if self.have_item(CATCH_SPECIAL_BALLS[t]):
                        return CATCH_SPECIAL_BALLS[t]

        for item in CATCH_BALL_PRIORITY:
            if self.have_item(item):
                return item

        return None


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

        self.rechecking = False

        self.settings = {}
        self.pending_purchases = []

        self.inventory = Inventory()

        self.load_settings()

        self.pokedex = Pokedex(self.discord)

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            to_write = {
                "inventory": self.inventory.get(),
                "settings": self.settings
            }
            if self.discord is not None:
                to_write["discord"] = self.discord
            f.write(json.dumps(to_write, indent=4))

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                j = json.load(f)
                self.inventory.set(j.get("inventory", {}))
                self.settings = j.get("settings", {})
                self.discord = j.get("discord", None)
        except:
            self.settings = {}

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

    def last_attempt(self, set_to=None, channel=None, have=None):
        if set_to is None:
            return self.last_catch, self.last_channel, self.last_have

        self.last_catch = set_to
        self.last_channel = channel
        self.last_have = have
        self.rechecking = False

    def set_rechecking(self, rechecking):
        self.rechecking = rechecking

    def get_catch_message(self, use=True, repeat=False):
        selected = self.inventory.get_catch_ball(self.last_type, repeat)

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

    def get_type_mission(self):
        m = self.settings.get("type_mission", None)
        t = self.settings.get("type_target", None)
        c = self.settings.get("type_caught", 0)
        return m, t, c

    def check_type_mission(self, inc=False):
        mission, target, caught = self.get_type_mission()
        is_type = False

        if mission in self.last_type:
            if target is None:
                is_type = True
            elif caught < target:
                is_type = True

        if is_type and inc:
            self.settings["type_caught"] = caught + 1

        return is_type
