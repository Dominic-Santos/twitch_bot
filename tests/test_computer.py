TEST_INVENTORY = [{
    "id": 16505571,
    "lvl": 14,
    "nickname": "Magikarp\u2640",
    "current_hp": 31,
    "max_hp": 31,
    "locked": False,
    "pokedexId": 10391,
    "order": 129,
    "baseStats": 200,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 16.833333333333332,
    "sellPrice": 103,
    "caughtAt": "2023-02-08T12:34:31.443Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Magikarp"
}, {
    "id": 13409144,
    "lvl": 14,
    "nickname": None,
    "current_hp": 29,
    "max_hp": 29,
    "locked": False,
    "pokedexId": 129,
    "order": 129,
    "baseStats": 200,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 14.666666666666666,
    "sellPrice": 90,
    "caughtAt": "2022-11-27T12:01:03.698Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Magikarp"
}, {
    "id": 15496549,
    "lvl": 14,
    "nickname": None,
    "current_hp": 34,
    "max_hp": 34,
    "locked": False,
    "pokedexId": 25,
    "order": 25,
    "baseStats": 320,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 13.166666666666666,
    "sellPrice": 185,
    "caughtAt": "2023-01-17T03:47:58.524Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Pikachu"
}, {
    "id": 16896546,
    "lvl": 4,
    "nickname": "tradeB\u2640",
    "current_hp": 20,
    "max_hp": 20,
    "locked": False,
    "pokedexId": 10372,
    "order": 229,
    "baseStats": 500,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 12.833333333333334,
    "sellPrice": 151,
    "caughtAt": "2023-02-17T22:04:14.582Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Houndoom"
}]

from . import COMPUTER


def test_have_by_name():
    test_cases = [
        ("Magikarp", True),
        ("Houndoom", True),
        ("Pikachu", True),
        ("Charmander", False),
        ("Dragonite", False),
    ]
    COMPUTER.set({"allPokemon": TEST_INVENTORY})

    for poke_name, expected in test_cases:
        assert COMPUTER.have(poke_name) == expected
