from . import POKEDEX


test_cases = [
    ("Charmander", ["Fire"]),
    ("Pikachu", ["Electric"]),
    ("Farfetch’d", ["Normal", "Flying"]),
    ("Mr. Mime", ["Psychic", "Fairy"]),
    ("Flabébé", ["Fairy"]),
    ("Fake Pokemon", []),
    ("Mime Jr.", ["Psychic", "Fairy"]),
    ("Rotom (Mow)", ["Electric", "Ghost"]),
    ("Aegislash (Shield)", ["Steel", "Ghost"])
]


def test_pokedex():
    for pokemon, expected in test_cases:
        p = POKEDEX.clean_name(pokemon)
        types = POKEDEX.get_type(p)
        assert types == expected
