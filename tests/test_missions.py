from . import Missions, Pokemon
import json

MISSIONS = Missions()

MISSIONS_STR = """{"missions": [{"name": "Wondertrade normal types", "goal": 6, "progress": 2, "rewardItem": {"id": 76, "name": "Normal Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "normal_stone", "category": "evolution", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "Participate in public battles using a grass type", "goal": 10, "progress": 12, "rewardItem": null, "rewardPokemon": {"id": 86321, "name": "His Voltorb", "description": "An enigmatic Pok\u00e9mon that happens to bear a resemblance to a Pok\u00e9 Ball. When excited, it discharges the electric current it has stored in its belly, then lets out a great, uproarious laugh.", "sprite_name": "hisuian-voltorb"}, "endDate": "9 minutes"}, {"name": "Win easy stadium battles", "goal": 5, "progress": 1, "rewardItem": {"id": 40, "name": "Hyper Potion", "description": "A spray-type medicine for treating wounds. It can be used to restore 120 HP to a single Pok\u00e9mon.", "sprite_name": "hyper_potion", "category": "heal", "tmType": null, "amount": 10}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "Miss catches", "goal": 12, "progress": 5, "rewardItem": {"id": 97, "name": "Stone Ball", "description": "A rare  ball with an increased chance to drop an evolution stone.", "sprite_name": "stone_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "???", "goal": 3, "progress": 6, "rewardItem": {"id": 79, "name": "Poison Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "poison_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "9 minutes"}], "endDate": "9 minutes"}"""
MISSIONS_STR_2 = """{"missions": [{"name": "Catch fire type pokemon", "goal": 5, "progress": 0, "rewardItem": null, "rewardPokemon": {"id": 4, "name": "Charmander", "description": "From the time it is born, a flame burns at the tip of its tail. Its life would end if the flame were to go out.", "sprite_name": "charmander"}, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "???", "goal": 2, "progress": 0, "rewardItem": {"id": 25, "name": "Timer Ball", "description": "A somewhat different Pok\u00e9 Ball that becomes progressively more effective at catching Pok\u00e9mon the closer the Pok\u00e9mon is to escaping.", "sprite_name": "timer_ball", "category": "ball", "tmType": null, "amount": 7}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Wondertrade Pok\u00e9mon with less than 383 BST", "goal": 10, "progress": 0, "rewardItem": {"id": 88, "name": "Electric Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "electric_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Use field effects in a battle", "goal": 2, "progress": 0, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pok\u00e9mon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Miss catches", "goal": 25, "progress": 26, "rewardItem": {"id": 94, "name": "Shimmering Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve.", "sprite_name": "shimmering_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}], "endDate": "6 days, 23 hours and 59 minutes"}"""
MISSIONS_JSON = json.loads(MISSIONS_STR)
MISSIONS_JSON_2 = json.loads(MISSIONS_STR_2)


def test_check_missions_case1():
    MISSIONS.set(MISSIONS_JSON)
    pokemon = Pokemon()
    pokemon.types = ["Normal", "Fairy"]
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 1
    assert len(wondertrade_reasons) == 1
    assert "miss" in reasons
    assert "type" in wondertrade_reasons
    assert MISSIONS.have_wondertrade_missions()


def test_check_missions_case2():
    MISSIONS.set(MISSIONS_JSON_2)
    pokemon = Pokemon()
    pokemon.types = ["Fire", "Fairy"]
    pokemon.bst = 200
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 1
    assert len(wondertrade_reasons) == 1
    assert "type" in reasons
    assert "bst" in wondertrade_reasons

    pokemon = Pokemon()
    pokemon.types = ["Fairy"]
    pokemon.bst = 900
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 0
    assert len(wondertrade_reasons) == 0
    assert MISSIONS.have_wondertrade_missions()
