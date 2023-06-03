from . import Missions, Pokemon
import json

MISSIONS = Missions()

MISSIONS_STR = """{"missions": [{"name": "Wondertrade normal types", "goal": 6, "progress": 2, "rewardItem": {"id": 76, "name": "Normal Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "normal_stone", "category": "evolution", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "Participate in public battles using a grass type", "goal": 10, "progress": 12, "rewardItem": null, "rewardPokemon": {"id": 86321, "name": "His Voltorb", "description": "An enigmatic Pok\u00e9mon that happens to bear a resemblance to a Pok\u00e9 Ball. When excited, it discharges the electric current it has stored in its belly, then lets out a great, uproarious laugh.", "sprite_name": "hisuian-voltorb"}, "endDate": "9 minutes"}, {"name": "Win easy stadium battles", "goal": 5, "progress": 1, "rewardItem": {"id": 40, "name": "Hyper Potion", "description": "A spray-type medicine for treating wounds. It can be used to restore 120 HP to a single Pok\u00e9mon.", "sprite_name": "hyper_potion", "category": "heal", "tmType": null, "amount": 10}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "Miss catches", "goal": 12, "progress": 5, "rewardItem": {"id": 97, "name": "Stone Ball", "description": "A rare  ball with an increased chance to drop an evolution stone.", "sprite_name": "stone_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "???", "goal": 3, "progress": 6, "rewardItem": {"id": 79, "name": "Poison Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "poison_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "9 minutes"}], "endDate": "9 minutes"}"""
MISSIONS_STR_2 = """{"missions": [{"name": "Catch fire type pokemon", "goal": 5, "progress": 0, "rewardItem": null, "rewardPokemon": {"id": 4, "name": "Charmander", "description": "From the time it is born, a flame burns at the tip of its tail. Its life would end if the flame were to go out.", "sprite_name": "charmander"}, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "???", "goal": 2, "progress": 0, "rewardItem": {"id": 25, "name": "Timer Ball", "description": "A somewhat different Pok\u00e9 Ball that becomes progressively more effective at catching Pok\u00e9mon the closer the Pok\u00e9mon is to escaping.", "sprite_name": "timer_ball", "category": "ball", "tmType": null, "amount": 7}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Wondertrade Pok\u00e9mon with less than 383 BST", "goal": 10, "progress": 0, "rewardItem": {"id": 88, "name": "Electric Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "electric_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Use field effects in a battle", "goal": 2, "progress": 0, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pok\u00e9mon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Miss catches", "goal": 25, "progress": 26, "rewardItem": {"id": 94, "name": "Shimmering Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve.", "sprite_name": "shimmering_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}], "endDate": "6 days, 23 hours and 59 minutes"}"""
MISSIONS_STR_3 = """{"missions": [{"name": "Catch Pokemon heavier than 250kg / 551 lbs", "goal": 3, "progress": 0, "rewardItem": {"id": 4, "name": "Ultra Ball", "description": "An ultra-high-performance Pok\u00e9 Ball that provides a higher success rate for catching Pok\u00e9mon than a Great Ball.", "sprite_name": "ultra_ball", "category": "ball", "tmType": null, "amount": 5}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Participate in public battles using a dark type", "goal": 10, "progress": 0, "rewardItem": null, "rewardPokemon": {"id": 258, "name": "Mudkip", "description": "In water, Mudkip breathes using the gills on its cheeks. If it is faced with a tight situation in battle, this Pok\u00e9mon will unleash its amazing power\u2014it can crush rocks bigger than itself.", "sprite_name": "mudkip"}, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Use super effective moves", "goal": 50, "progress": 0, "rewardItem": {"id": 51, "name": "Team enhancer", "description": "Use this item to increase the amount of teams by 1! You can have up to 20 teams.", "sprite_name": "team_enhancer", "category": "extra", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Wonder trade ground type Pok\u00e9mon", "goal": 7, "progress": 1, "rewardItem": {"id": 80, "name": "Ground Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "ground_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Catch ghost type Pok\u00e9mon", "goal": 5, "progress": 0, "rewardItem": {"id": 83, "name": "Ghost Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "ghost_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}], "endDate": "6 days, 15 hours and 31 minutes"}"""
MISSIONS_STR_4 = """{"missions": [{"name": "Catch psychic type Pok\u00e9mon", "goal": 7, "progress": 0, "rewardItem": {"id": 29, "name": "Clone Ball", "description": "An experimental Ball which generates a second Pokemon from the one you originally catch with this ball", "sprite_name": "clone_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Miss a catch", "goal": 15, "progress": 11, "rewardItem": {"id": 25, "name": "Timer Ball", "description": "A somewhat different Pok\u00e9 Ball that becomes progressively more effective at catching Pok\u00e9mon the closer the Pok\u00e9mon is to escaping.", "sprite_name": "timer_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Wondertrade", "goal": 20, "progress": 3, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pok\u00e9mon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Attempt catches", "goal": 50, "progress": 38, "rewardItem": {"id": 86, "name": "Water Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "water_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Catch Pok\u00e9mon with less than 333 BST", "goal": 10, "progress": 7, "rewardItem": {"id": 54, "name": "Total Reset", "description": "Total Reset used to teach your Pok\u00e9mon a full new move set, completely changes the nature of your pokemon and changes the individual values of a Pok\u00e9mon. Use it with caution.", "sprite_name": "total_reset", "category": "battle", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Participate in public battles using a dragon type", "goal": 15, "progress": 0, "rewardItem": {"id": 2, "name": "Poke Ball", "description": "A device for catching wild Pok\u00e9mon. It's thrown like a ball at a Pok\u00e9mon, comfortably encapsulating its target.", "sprite_name": "poke_ball", "category": "ball", "tmType": null, "amount": 10}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}], "endDate": "6 days, 14 hours and 9 minutes"}"""
MISSIONS_STR_5 = """{"missions": [{"name": "Use super effective moves", "goal": 75, "progress": 0, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pok\u00e9mon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Participate in public battles using a water type", "goal": 10, "progress": 0, "rewardItem": {"id": 24, "name": "Net Ball", "description": "A somewhat different Pok\u00e9 Ball that is more effective when attempting to catch Water- or Bug-type Pok\u00e9mon.", "sprite_name": "net_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Catch Pokemon heavier than 250kg / 551 lbs", "goal": 2, "progress": 0, "rewardItem": {"id": 49, "name": "Present", "description": "Enter a chat and type !pokegift to make other players happy! \ud83c\udf85", "sprite_name": "present", "category": "event", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Attempt catches", "goal": 35, "progress": 43, "rewardItem": null, "rewardPokemon": {"id": 816, "name": "Sobble", "description": "When it gets wet, its skin changes color, and this Pok\u00e9mon becomes invisible as if it were camouflaged.", "sprite_name": "sobble"}, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Wondertrade steel types", "goal": 8, "progress": 5, "rewardItem": {"id": 84, "name": "Steel Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "steel_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 25, "progress": 24, "rewardItem": null, "rewardPokemon": {"id": 382, "name": "Kyogre", "description": "Kyogre is said to be the personification of the sea itself. Legends tell of its many clashes against Groudon, as each sought to gain the power of nature.", "sprite_name": "kyogre"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 15, "progress": 24, "rewardItem": null, "rewardPokemon": {"id": 8, "name": "Wartortle", "description": "It cleverly controls its furry ears and tail to maintain its balance while swimming.", "sprite_name": "wartortle"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 100% bigger than average!", "goal": 1, "progress": 0, "rewardItem": {"id": "hidden_item", "name": "???", "description": "???", "sprite_name": "hidden_item", "category": "extra", "tmType": null, "amount": 0}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 25% smaller and 25% lighter!", "goal": 1, "progress": 3, "rewardItem": {"id": 94, "name": "Shimmering Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve.", "sprite_name": "shimmering_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 10, "progress": 24, "rewardItem": {"id": 102, "name": "TM Bubble Beam", "description": "Teaches a water type Pok\u00e9mon the move Bubble Beam. Randomly replaces one of the pokemon's water moves.", "sprite_name": "tm_bubble_beam", "category": "tm", "tmType": "water", "amount": 1}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 75% smaller than average!", "goal": 1, "progress": 1, "rewardItem": null, "rewardPokemon": {"id": 657, "name": "Frogadier", "description": "Its swiftness is unparalleled. It can scale a tower of more than 2,000 feet in a minute\u2019s time.", "sprite_name": "frogadier"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 1, "progress": 24, "rewardItem": {"id": 101, "name": "Dive Ball", "description": "A Ball that is more effective when attempting to catch\ud83d\udc1f Fish \ud83d\udc1fPok\u00e9mon.", "sprite_name": "dive_ball", "category": "ball", "tmType": null, "amount": 15}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 5, "progress": 24, "rewardItem": {"id": 18, "name": "Great Cherish Ball", "description": "A modified Cherish Ball with a better catch rate. Has a higher chance to catch a shiny Pokemon.", "sprite_name": "great_cherish_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 50% bigger than average!", "goal": 1, "progress": 2, "rewardItem": null, "rewardPokemon": {"id": 158, "name": "Totodile", "description": "Despite the smallness of its body, Totodile\u2019s jaws are very powerful. While the Pok\u00e9mon may think it is just playfully nipping, its bite has enough power to cause serious injury.", "sprite_name": "totodile"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 100% heavier than average!", "goal": 1, "progress": 0, "rewardItem": {"id": "hidden_item", "name": "???", "description": "???", "sprite_name": "hidden_item", "category": "extra", "tmType": null, "amount": 0}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 75% lighter than average!", "goal": 1, "progress": 3, "rewardItem": null, "rewardPokemon": {"id": 490, "name": "Manaphy", "description": "It starts its life with a wondrous power that permits it to bond with any kind of Pok\u00e9mon.", "sprite_name": "manaphy"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 50% heavier than average!", "goal": 1, "progress": 4, "rewardItem": null, "rewardPokemon": {"id": 80, "name": "Slowbro", "description": "If this Pok\u00e9mon squeezes the tongue of the Shellder biting it, the Shellder will launch a toxic liquid from the tip of its shell.", "sprite_name": "slowbro"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 20, "progress": 24, "rewardItem": {"id": 101, "name": "Dive Ball", "description": "A Ball that is more effective when attempting to catch\ud83d\udc1f Fish \ud83d\udc1fPok\u00e9mon.", "sprite_name": "dive_ball", "category": "ball", "tmType": null, "amount": 15}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}], "endDate": "6 days, 8 hours and 49 minutes"}"""
MISSIONS_JSON = json.loads(MISSIONS_STR)
MISSIONS_JSON_2 = json.loads(MISSIONS_STR_2)
MISSIONS_JSON_3 = json.loads(MISSIONS_STR_3)
MISSIONS_JSON_4 = json.loads(MISSIONS_STR_4)
MISSIONS_JSON_5 = json.loads(MISSIONS_STR_5)


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


def test_check_missions_completed():
    MISSIONS.set(MISSIONS_JSON)
    tmp_missions = {"missions": []}
    mission_title = "Wondertrade normal types"

    for mission in MISSIONS_JSON["missions"]:
        if mission["name"] == mission_title:
            mission_goal = mission["goal"]
            mission["progress"] = mission_goal
            reward = mission["rewardItem"]["name"]
            reward_amount = mission["rewardItem"]["amount"]
        tmp_missions["missions"].append(mission)

    MISSIONS.set(tmp_missions)

    completed = MISSIONS.get_completed()
    assert len(completed) == 1
    assert completed[0][0] == f"{mission_title} ({mission_goal})"
    assert completed[0][1]["reward"] == f"{reward_amount} {reward}"


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


def test_check_missions_case3():
    MISSIONS.set(MISSIONS_JSON_3)
    pokemon = Pokemon()
    pokemon.types = ["Ghost", "Ground"]
    pokemon.weight = 300
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 2
    assert len(wondertrade_reasons) == 1
    assert "type" in reasons
    assert "weight" in reasons
    assert "type" in wondertrade_reasons


def test_check_missions_case4():
    MISSIONS.set(MISSIONS_JSON_4)
    missions = MISSIONS.data
    assert len(missions.keys()) == 4
    assert len(missions.get("bst", [])) == 1
    assert missions.get("bst", [(0, 0)])[0] == (0, 333)
    assert len(missions.get("type", [])) == 1
    assert missions.get("type", ["none"])[0] == "Psychic"
    assert missions.get("attempt", False) == True
    assert missions.get("miss", False) == True


def test_check_missions_case5_fish():
    MISSIONS.set(MISSIONS_JSON_5)
    missions = MISSIONS.data
    assert missions.get("fish", False) == True
    assert missions.get("weight", [(0, 0)])[0] == (250, 9999)
