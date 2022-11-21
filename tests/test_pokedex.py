from . import POKEDEX


test_cases = [
    ("Charmander", ["Fire"]),
    ("Pikachu", ["Electric"]),
    ("Farfetch’d", ["Normal", "Flying"]),
    ("Mr. Mime", ["Psychic", "Fairy"]),
    ("Fake Pokemon", []),
]


def test_pokedex():
    for pokemon, expected in test_cases:
        p = POKEDEX.clean_name(pokemon)
        types = POKEDEX.get_type(p)
        assert types == expected
