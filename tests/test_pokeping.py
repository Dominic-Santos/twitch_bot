ALTER = {
    "content": "** ID: 10369 | <@&1068127190614552667> | Hippopotas-female **",
    "mention_roles": [
        "1068127190614552667"
    ],
    "timestamp": "2023-02-22T22:19:19.764000+00:00"
}

NORMAL = {
    "content": "Hippopotas - <@&935874437574688778> - <@&935906365434634320> 330 - 49.5 KG ! <@&936750563473891408> | <@&967919166667513877>",
    "mention_roles": [
        "935906365434634320",
        "935874437574688778",
        "936750563473891408",
        "967919166667513877"
    ],
    "timestamp": "2023-02-22T22:19:15.235000+00:00"
}

BST_ROLE = {
    "content": "Copperajah - <@&935874381316522014> - <@&935906659199500338> <@&960299429288620173> - 650.0 KG - Heavy Ball ! <@&937386694573977692> + <@&950160825115623464> ++ <@&995842704099508294>",
    "mention_roles": [
        "995842704099508294",
        "950160825115623464",
        "960299429288620173",
        "935906659199500338",
        "937386694573977692",
        "935874381316522014"
    ],
    "timestamp": "2023-02-23T06:19:16.192000+00:00"
}

MISSIGNO = {
    "content": "ID 10112: @MissingNo. delay: 7 seconds",
    "mention_roles": [],
    "timestamp": "2023-02-23T06:19:16.192000+00:00"
}

from . import Pokemon, PokemonCG

POKEMON = PokemonCG.PokemonComunityGame()
# PING = Pokeping()


def test_normal():
    pokemon = POKEMON.pokeping.parse_pokemon(NORMAL)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "Hippopotas"
    assert pokemon.is_alternate is False
    assert pokemon.pokemon_id == 0
    assert pokemon.alt_name == "NA"
    assert pokemon.bst == 330
    assert pokemon.weight == 49.5


def test_alter_half():
    pokemon = POKEMON.pokeping.parse_pokemon(ALTER)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "NA"
    assert pokemon.is_alternate
    assert pokemon.pokemon_id == 10369
    assert pokemon.alt_name == "Hippopotas-female"
    assert pokemon.bst == -1
    assert pokemon.weight == -1


def test_bst_role():
    pokemon = POKEMON.pokeping.parse_pokemon(BST_ROLE)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "Copperajah"
    assert pokemon.is_alternate is False
    assert pokemon.pokemon_id == 0
    assert pokemon.alt_name == "NA"
    assert pokemon.bst == 500
    assert pokemon.weight == 650.0


def test_missingno():
    pokemon = POKEMON.pokeping.parse_pokemon(MISSIGNO)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "NA"
    assert pokemon.is_alternate is False
    assert pokemon.pokemon_id == 10112
    assert pokemon.alt_name == "NA"
    assert pokemon.bst == -1
    assert pokemon.weight == -1
