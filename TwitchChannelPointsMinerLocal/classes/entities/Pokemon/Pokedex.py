import requests
import json
from bs4 import BeautifulSoup

from .Pokeping import Pokeping

POKEMON_INFO_URL = "https://www.pokemon.com/us/pokedex/{pokemon}"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
POKEDEX_FILE = "pokedex.json"

POKEMON_TIERS = {
    "S": ["Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune", "Lugia", "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect", "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion", "Type:Null", "Silvally", "TapuKoko", "TapuLele", "TapuBulu", "TapuFini", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", "Kartana", "Guzzlord", "Necrozma", "Magearna", "Marshadow", "Poipole", "Naganadel", "Stakataka", "Blacephalon", "Zeraora", "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex", "Ting-lu", "Chien-pao", "Wo-chien", "Chi-yu", "Koraidon", "Miraidon"],
    "A": ["Raichu", "Nidoqueen", "Nidoking", "Vileplume", "Arcanine", "Poliwrath", "Alakazam", "Machamp", "Victreebel", "Golem", "Gengar", "Starmie", "Gyarados", "Lapras", "Vaporeon", "Jolteon", "Flareon", "Aerodactyl", "Snorlax", "Dragonite", "Crobat", "Politoed", "Espeon", "Umbreon", "Slowking", "Steelix", "Scizor", "Kingdra", "Blissey", "Pupitar", "Tyranitar", "Ludicolo", "Shiftry", "Gardevoir", "Slaking", "Aggron", "Wailord", "Camerupt", "Flygon", "Altaria", "Milotic", "Walrein", "Salamence", "Metagross", "Luxray", "Roserade", "Rampardos", "Bastiodon", "Vespiquen", "Drifblim", "Mismagius", "Honchkrow", "Spiritomb", "Garchomp", "Lucario", "Hippowdon", "Toxicroak", "Abomasnow", "Weavile", "Magnezone", "Lickilicky", "Rhyperior", "Electivire", "Magmortar", "Togekiss", "Yanmega", "Leafeon", "Glaceon", "Gliscor", "Mamoswine", "Porygon-Z", "Gallade", "Dusknoir", "Froslass", "Rotom", "Gigalith", "Excadrill", "Conkeldurr", "Seismitoad", "Leavanny", "Scolipede", "Krookodile", "Darmanitan", "Cofagrigus", "Archeops", "Zoroark", "Gothitelle", "Reuniclus", "Vanilluxe", "Ferrothorn", "Klinklang", "Eelektross", "Chandelure", "Haxorus", "Druddigon", "Golurk", "Bisharp", "Hydreigon", "Volcarona", "Talonflame", "Pyroar", "Florges", "Pangoro", "Aegislash", "Dragalge", "Tyrantrum", "Sylveon", "Hawlucha", "Goodra", "Noivern", "Toucannon", "Vikavolt", "Toxapex", "Salazzle", "Bewear", "Tsareena", "Golisopod", "Turtonator", "Mimikyu", "Kommo-o", "Corviknight", "Orbeetle", "Coalossal", "Flapple", "Appletun", "Toxtricity", "Centiskorch", "Polteageist", "Hatterene", "Grimmsnarl", "Obstagoon", "Cursola", "Mr-Rime", "Runerigus", "Alcremie", "Copperajah", "Duraludon", "Drakloak", "Dragapult", "Farigiraf", "Dondozo", "Arboliva", "Revavroom", "Cetitan", "Baxcalibur", "Cyclizar", "Pawmot", "Flamigo", "Garganacl", "Glimmora", "Mabosstiff", "Gholdengo", "GreatTusk", "BruteBonnet", "SandyShocks", "ScreamTail", "FlutterMane", "SlitherWing", "RoaringMoon", "IronTreads", "IronMoth", "IronHands", "IronJugulis", "IronThorns", "IronBundle", "IronValiant", "Tinkaton", "Armarouge", "Ceruledge", "Kingambit", "Annihilape"],
    "B": ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Butterfree", "Beedrill", "Pidgeotto", "Pidgeot", "Raticate", "Fearow", "Arbok", "Pikachu", "Sandslash", "Nidorina", "Nidorino", "Clefable", "Ninetales", "Wigglytuff", "Gloom", "Parasect", "Venomoth", "Dugtrio", "Persian", "Golduck", "Primeape", "Poliwhirl", "Kadabra", "Machoke", "Weepinbell", "Tentacruel", "Graveler", "Rapidash", "Slowbro", "Magneton", "Dodrio", "Dewgong", "Muk", "Cloyster", "Haunter", "Hypno", "Kingler", "Electrode", "Exeggutor", "Marowak", "Hitmonlee", "Hitmonchan", "Weezing", "Rhydon", "Seadra", "Seaking", "Scyther", "Electabuzz", "Magmar", "Pinsir", "Eevee", "Porygon", "Omastar", "Kabutops", "Dratini", "Dragonair", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Furret", "Noctowl", "Ledian", "Ariados", "Lanturn", "Pichu", "Togetic", "Xatu", "Flaaffy", "Ampharos", "Bellossom", "Azumarill", "Skiploom", "Jumpluff", "Sunflora", "Quagsire", "Wobbuffet", "Forretress", "Granbull", "Heracross", "Ursaring", "Magcargo", "Piloswine", "Octillery", "Skarmory", "Houndoom", "Donphan", "Porygon2", "Hitmontop", "Larvitar", "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", "Swampert", "Mightyena", "Linoone", "Beautifly", "Dustox", "Lombre", "Nuzleaf", "Swellow", "Pelipper", "Kirlia", "Masquerain", "Breloom", "Vigoroth", "Shedinja", "Loudred", "Exploud", "Hariyama", "Delcatty", "Lairon", "Medicham", "Manectric", "Swalot", "Sharpedo", "Torkoal", "Grumpig", "Trapinch", "Vibrava", "Cacturne", "Zangoose", "Seviper", "Whiscash", "Crawdaunt", "Claydol", "Cradily", "Armaldo", "Feebas", "Castform", "Kecleon", "Banette", "Dusclops", "Tropius", "Chimecho", "Absol", "Glalie", "Sealeo", "Huntail", "Gorebyss", "Relicanth", "Bagon", "Shelgon", "Beldum", "Metang", "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", "Empoleon", "Staravia", "Staraptor", "Bibarel", "Kricketune", "Luxio", "Wormadam", "Mothim", "Pachirisu", "Floatzel", "Cherrim", "Gastrodon", "Ambipom", "Lopunny", "Purugly", "Skuntank", "Bronzong", "Gible", "Gabite", "Riolu", "Drapion", "Carnivine", "Lumineon", "Tangrowth", "Probopass", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", "Oshawott", "Dewott", "Samurott", "Watchog", "Herdier", "Stoutland", "Liepard", "Simisage", "Simisear", "Simipour", "Musharna", "Tranquill", "Unfezant", "Zebstrika", "Boldore", "Swoobat", "Audino", "Gurdurr", "Palpitoad", "Throh", "Sawk", "Swadloon", "Whirlipede", "Whimsicott", "Lilligant", "Krokorok", "Crustle", "Scrafty", "Sigilyph", "Yamask", "Carracosta", "Garbodor", "Zorua", "Cinccino", "Gothorita", "Duosion", "Swanna", "Vanillish", "Sawsbuck", "Emolga", "Escavalier", "Amoonguss", "Jellicent", "Alomomola", "Galvantula", "Klang", "Eelektrik", "Beheeyem", "Lampent", "Axew", "Fraxure", "Beartic", "Cryogonal", "Accelgor", "Mienshao", "Bouffalant", "Braviary", "Mandibuzz", "Heatmor", "Durant", "Deino", "Zweilous", "Larvesta", "Chespin", "Quilladin", "Chesnaught", "Fennekin", "Braixen", "Delphox", "Froakie", "Frogadier", "Greninja", "Diggersby", "Fletchinder", "Spewpa", "Vivillon", "Floette", "Gogoat", "Meowstic", "Honedge", "Doublade", "Aromatisse", "Slurpuff", "Malamar", "Clawitzer", "Heliolisk", "Aurorus", "Dedenne", "Carbink", "Sliggoo", "Trevenant", "Gourgeist", "Avalugg", "Rowlet", "Dartrix", "Decidueye", "Litten", "Torracat", "Incineroar", "Popplio", "Brionne", "Primarina", "Trumbeak", "Gumshoos", "Charjabug", "Crabominable", "Ribombee", "Lycanroc", "Mudsdale", "Araquanid", "Lurantis", "Shiinotic", "Steenee", "Oranguru", "Passimian", "Palossand", "Minior", "Bruxish", "Drampa", "Dhelmise", "Jangmo-o", "Hakamo-o", "Grookey", "Thwackey", "Rillaboom", "Scorbunny", "Raboot", "Cinderace", "Sobble", "Drizzile", "Inteleon", "Dottler", "Thievul", "Eldegoss", "Dubwool", "Drednaw", "Boltund", "Carkol", "Applin", "Sandaconda", "Barraskewda", "Grapploct", "Hattrem", "Morgrem", "Sirfetch’d", "Frosmoth", "Stonjourner", "Eiscue", "Indeedee", "Morpeko", "Dracozolt", "Arctozolt", "Dracovish", "Arctovish", "Dreepy", "Sprigatito", "Floragato", "Meowscarada", "Fuecoco", "Crocalor", "Skeledirge", "Quaxly", "Quaxwell", "Quaquaval", "Oinkologne", "Dudunsparce", "Spidops", "Lokix", "Rabsca", "Houndstone", "Espathra", "Wugtrio", "Veluza", "Palafin", "Dolliv", "Scovillain", "Bellibolt", "Orthworm", "Maushold", "Arctibax", "Tatsugiri", "Pawmo", "Kilowattrel", "Bombirdier", "Klawf", "Naclstack", "Grafaiai", "Dachsbun", "Brambleghast", "Tinkatuff", "Toedscruel", "Clodsire"],
    "C": ["Caterpie", "Metapod", "Weedle", "Kakuna", "Pidgey", "Rattata", "Spearow", "Ekans", "Sandshrew", "Nidoran-female", "Nidoran-male", "Clefairy", "Vulpix", "Jigglypuff", "Zubat", "Golbat", "Oddish", "Paras", "Venonat", "Diglett", "Meowth", "Psyduck", "Mankey", "Growlithe", "Poliwag", "Abra", "Machop", "Bellsprout", "Tentacool", "Geodude", "Ponyta", "Slowpoke", "Magnemite", "Farfetch’d", "Doduo", "Seel", "Grimer", "Shellder", "Gastly", "Onix", "Drowzee", "Krabby", "Voltorb", "Exeggcute", "Cubone", "Lickitung", "Koffing", "Rhyhorn", "Chansey", "Tangela", "Kangaskhan", "Horsea", "Goldeen", "Staryu", "Mr.Mime", "Jynx", "Tauros", "Magikarp", "Ditto", "Omanyte", "Kabuto", "Sentret", "Hoothoot", "Ledyba", "Spinarak", "Chinchou", "Cleffa", "Igglybuff", "Togepi", "Natu", "Mareep", "Marill", "Sudowoodo", "Hoppip", "Aipom", "Sunkern", "Yanma", "Wooper", "Murkrow", "Misdreavus", "Unown", "Girafarig", "Pineco", "Dunsparce", "Gligar", "Snubbull", "Qwilfish", "Shuckle", "Sneasel", "Teddiursa", "Slugma", "Swinub", "Corsola", "Remoraid", "Delibird", "Mantine", "Houndour", "Phanpy", "Stantler", "Smeargle", "Tyrogue", "Smoochum", "Elekid", "Magby", "Miltank", "Poochyena", "Zigzagoon", "Wurmple", "Silcoon", "Cascoon", "Lotad", "Seedot", "Taillow", "Wingull", "Ralts", "Surskit", "Shroomish", "Slakoth", "Nincada", "Ninjask", "Whismur", "Makuhita", "Azurill", "Nosepass", "Skitty", "Sableye", "Mawile", "Aron", "Meditite", "Electrike", "Plusle", "Minun", "Volbeat", "Illumise", "Roselia", "Gulpin", "Carvanha", "Wailmer", "Numel", "Spoink", "Spinda", "Cacnea", "Swablu", "Lunatone", "Solrock", "Barboach", "Corphish", "Baltoy", "Lileep", "Anorith", "Shuppet", "Duskull", "Wynaut", "Snorunt", "Spheal", "Clamperl", "Luvdisc", "Starly", "Bidoof", "Kricketot", "Shinx", "Budew", "Cranidos", "Shieldon", "Burmy", "Combee", "Buizel", "Cherubi", "Shellos", "Drifloon", "Buneary", "Glameow", "Chingling", "Stunky", "Bronzor", "Bonsly", "MimeJr.", "Happiny", "Chatot", "Munchlax", "Hippopotas", "Skorupi", "Croagunk", "Finneon", "Mantyke", "Snover", "Patrat", "Lillipup", "Purrloin", "Pansage", "Pansear", "Panpour", "Munna", "Pidove", "Blitzle", "Roggenrola", "Woobat", "Drilbur", "Timburr", "Tympole", "Sewaddle", "Venipede", "Cottonee", "Petilil", "Basculin", "Sandile", "Darumaka", "Maractus", "Dwebble", "Scraggy", "Tirtouga", "Archen", "Trubbish", "Minccino", "Gothita", "Solosis", "Ducklett", "Vanillite", "Deerling", "Karrablast", "Foongus", "Frillish", "Joltik", "Ferroseed", "Klink", "Tynamo", "Elgyem", "Litwick", "Cubchoo", "Shelmet", "Stunfisk", "Mienfoo", "Golett", "Pawniard", "Rufflet", "Vullaby", "Bunnelby", "Fletchling", "Scatterbug", "Litleo", "Flabebe", "Skiddo", "Pancham", "Furfrou", "Espurr", "Spritzee", "Swirlix", "Inkay", "Binacle", "Barbaracle ", "Skrelp", "Clauncher", "Helioptile", "Tyrunt", "Amaura", "Goomy", "Klefki", "Phantump", "Pumpkaboo", "Bergmite", "Noibat", "Pikipek", "Yungoos", "Grubbin", "Crabrawler", "Oricorio", "Cutiefly", "Rockruff", "Wishiwashi", "Mareanie", "Mudbray", "Dewpider", "Fomantis", "Morelull", "Salandit", "Stufful", "Bounsweet", "Comfey", "Wimpod", "Sandygast", "Pyukumuku", "Komala", "Togedemaru", "Skwovet", "Greedent", "Rookidee", "Corvisquire", "Blipbug", "Nickit", "Gossifleur", "Wooloo", "Chewtle", "Yamper", "Rolycoly", "Silicobra", "Cramorant", "Arrokuda", "Toxel", "Sizzlipede", "Clobbopus", "Sinistea", "Hatenna", "Impidimp", "Perrserker", "Milcery", "Falinks", "Pincurchin", "Snom", "Cufant", "Lechonk", "Tarountula", "Nymble", "Rellor", "Greavard", "Flittle", "Wiglett", "Finizen", "Smoliv", "Capsakid", "Tadbulb", "Varoom", "Tandemaus", "Cetoddle", "Frigibax", "Pawmi", "Wattrel", "Squawkabilly", "Nacli", "Glimmet", "Shroodle", "Fidough", "Maschiff", "Bramblin", "Gimmighoul", "Tinkatink", "Charcadet", "Toedscool"]
}


class Pokedex(Pokeping):
    def __init__(self):
        super().__init__()
        self.types = {}
        self.alts = []
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
        elif " (" in pokemon:
            end = pokemon.split(" (")[0]
        elif pokemon.startswith("Mime"):
            end = "Mime-jr"
        elif pokemon.startswith("Mr"):
            end = "Mr-{poke}".format(poke=pokemon.split(" ")[1])
        end = end.replace("’", "")
        return end

    def alternate_caught(self, alt_id):
        if alt_id not in self.alts and alt_id != "0":
            self.alts.append(alt_id)

    def need_alternate(self, alt_id):
        return alt_id not in self.alts

    @staticmethod
    def tier(pokemon):
        for k in POKEMON_TIERS.keys():
            if pokemon in POKEMON_TIERS[k]:
                return k
        return None
