import json

from . import Pokedex

JSON_FILE = "tests/pokedex.json"

REGION_VARIANTS = ["Sin Gliscor", "His Braviary", "His Zoroark", "His Voltorb", "Hisuian Braviary", "Gal Rapidash", "Gal Darmanitan", "Gal Weezing", "Galarian Weezing"]
STARTER_POKEMON = ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", "Swampert", "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", "Empoleon", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", "Oshawott", "Dewott", "Samurott", "Chespin", "Quilladin", "Chesnaught", "Fennekin", "Braixen", "Delphox", "Froakie", "Frogadier", "Greninja", "Rowlet", "Dartrix", "Decidueye", "Litten", "Torracat", "Incineroar", "Popplio", "Brionne", "Primarina", "Grookey", "Thwackey", "Rillaboom", "Scorbunny", "Raboot", "Cinderace", "Sobble", "Drizzile", "Inteleon"]
LEGENDARY_POKEMON = ["Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune", "Lugia", "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect", "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion", "Type: Null", "Silvally", "Tapu Koko", "Tapu Lele", "Tapu Bulu", "Tapu Fini", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", "Kartana", "Guzzlord", "Necrozma", "Magearna", "Marshadow", "Poipole", "Naganadel", "Stakataka", "Blacephalon", "Zeraora", "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex", "Sin Kartana"]

FAIL_TO_FIND = None
pokedex = Pokedex()


def load_pokedex():
    with open(JSON_FILE) as of:
        data = json.load(of)
    return data


def test_tiers():
    dex_json = load_pokedex()

    for pokemon in dex_json["dex"]:
        assert pokedex.tier(pokemon["name"]) != FAIL_TO_FIND

    assert pokedex.tier("fakepokemon") == FAIL_TO_FIND
    assert pokedex.tier("Rotom (Mow)") != FAIL_TO_FIND


def test_regional():
    for pokemon in REGION_VARIANTS:
        assert pokedex.tier(pokemon) != FAIL_TO_FIND


def test_starter():
    for pokemon in STARTER_POKEMON:
        assert pokedex.tier(pokemon) != FAIL_TO_FIND


def test_legendary():
    for pokemon in LEGENDARY_POKEMON:
        assert pokedex.tier(pokemon) != FAIL_TO_FIND