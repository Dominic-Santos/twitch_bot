ALTER = {
    "id": "1078078565574254672",
    "type": 0,
    "content": "** ID: 10369 | <@&1068127190614552667> | Hippopotas-female **",
    "channel_id": "935704401954349196",
    "author":
    {
        "id": "935703703338483742",
        "username": "poke_ping",
        "display_name": None,
        "avatar": "168e60057d04a5bc6f8c8dca21781fec",
        "avatar_decoration": None,
        "discriminator": "9023",
        "public_flags": 0,
        "bot": True
    },
    "attachments":
    [],
    "embeds":
    [],
    "mentions":
    [],
    "mention_roles":
    [
        "1068127190614552667"
    ],
    "pinned": False,
    "mention_everyone": False,
    "tts": False,
    "timestamp": "2023-02-22T22:19:19.764000+00:00",
    "edited_timestamp": None,
    "flags": 0,
    "components":
    [],
    "reactions":
    [
        {
            "emoji":
            {
                "id": None,
                "name": "♀️"
            },
            "count": 3,
            "count_details":
            {
                "burst": 0,
                "normal": 3
            },
            "burst_user_ids":
            [],
            "burst_count": 0,
            "burst_colors":
            [],
            "burst_me": False,
            "me_burst": False,
            "me": False
        }
    ]
}
NORMAL = {
    "id": "1078078546578255893",
    "type": 0,
    "content": "Hippopotas - <@&935874437574688778> - <@&935906365434634320> 330 - 49.5 KG ! <@&936750563473891408> | <@&967919166667513877>",
    "channel_id": "935704401954349196",
    "author":
    {
        "id": "935703703338483742",
        "username": "poke_ping",
        "display_name": None,
        "avatar": "168e60057d04a5bc6f8c8dca21781fec",
        "avatar_decoration": None,
        "discriminator": "9023",
        "public_flags": 0,
        "bot": True
    },
    "attachments":
    [],
    "embeds":
    [],
    "mentions":
    [],
    "mention_roles":
    [
        "935906365434634320",
        "935874437574688778",
        "936750563473891408",
        "967919166667513877"
    ],
    "pinned": False,
    "mention_everyone": False,
    "tts": False,
    "timestamp": "2023-02-22T22:19:15.235000+00:00",
    "edited_timestamp": None,
    "flags": 0,
    "components":
    []
}
BST_ROLE = {
    "id": "1078199346547404880",
    "type": 0,
    "content": "Copperajah - <@&935874381316522014> - <@&935906659199500338> <@&960299429288620173> - 650.0 KG - Heavy Ball ! <@&937386694573977692> + <@&950160825115623464> ++ <@&995842704099508294>",
    "channel_id": "935704401954349196",
    "author":
    {
        "id": "935703703338483742",
        "username": "poke_ping",
        "display_name": None,
        "avatar": "168e60057d04a5bc6f8c8dca21781fec",
        "avatar_decoration": None,
        "discriminator": "9023",
        "public_flags": 0,
        "bot": True
    },
    "attachments":
    [],
    "embeds":
    [],
    "mentions":
    [],
    "mention_roles":
    [
        "995842704099508294",
        "950160825115623464",
        "960299429288620173",
        "935906659199500338",
        "937386694573977692",
        "935874381316522014"
    ],
    "pinned": False,
    "mention_everyone": False,
    "tts": False,
    "timestamp": "2023-02-23T06:19:16.192000+00:00",
    "edited_timestamp": None,
    "flags": 0,
    "components":
    [],
    "reactions":
    []
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
    assert pokemon.bst == 0
    assert pokemon.weight == 0


def test_bst_role():
    pokemon = POKEMON.pokeping.parse_pokemon(BST_ROLE)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "Copperajah"
    assert pokemon.is_alternate is False
    assert pokemon.pokemon_id == 0
    assert pokemon.alt_name == "NA"
    assert pokemon.bst == 500
    assert pokemon.weight == 650.0
