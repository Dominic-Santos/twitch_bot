"""
Todo:
    catch pokemon with X ball
    confirm attemp message

Done:
    Wondertrade <Type>
    Wondertrade <Bst>
    Catch Attempts
    Catch <Type>
    Catch <Weight>
    Miss Catches

"""

"""
{
    "missions": [
        {
            "name": "Catch Pokemon heavier than 250kg / 551 lbs",
            "goal": 3,
            "progress": 4,
            "rewardItem": {
                "id": 4,
                "name": "Ultra Ball",
                "description": "An ultra-high-performance Pok\u00e9 Ball that provides a higher success rate for catching Pok\u00e9mon than a Great Ball.",
                "sprite_name": "ultra_ball",
                "category": "ball",
                "tmType": null,
                "amount": 5
            },
            "rewardPokemon": null,
            "endDate": "12 hours and 8 minutes"
        },
        {
            "name": "Participate in public battles using a dark type",
            "goal": 10,
            "progress": 2,
            "rewardItem": null,
            "rewardPokemon": {
                "id": 258,
                "name": "Mudkip",
                "description": "In water, Mudkip breathes using the gills on its cheeks. If it is faced with a tight situation in battle, this Pok\u00e9mon will unleash its amazing power\u2014it can crush rocks bigger than itself.",
                "sprite_name": "mudkip"
            },
            "endDate": "12 hours and 8 minutes"
        },
        {
            "name": "Use super effective moves",
            "goal": 50,
            "progress": 2,
            "rewardItem": {
                "id": 51,
                "name": "Team enhancer",
                "description": "Use this item to increase the amount of teams by 1! You can have up to 20 teams.",
                "sprite_name": "team_enhancer",
                "category": "extra",
                "tmType": null,
                "amount": 2
            },
            "rewardPokemon": null,
            "endDate": "12 hours and 8 minutes"
        },
        {
            "name": "Wonder trade ground type Pok\u00e9mon",
            "goal": 7,
            "progress": 25,
            "rewardItem": {
                "id": 80,
                "name": "Ground Stone",
                "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
                "sprite_name": "ground_stone",
                "category": "evolution",
                "tmType": null,
                "amount": 1
            },
            "rewardPokemon": null,
            "endDate": "12 hours and 8 minutes"
        },
        {
            "name": "Catch ghost type Pok\u00e9mon",
            "goal": 5,
            "progress": 7,
            "rewardItem": {
                "id": 83,
                "name": "Ghost Stone",
                "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
                "sprite_name": "ghost_stone",
                "category": "evolution",
                "tmType": null,
                "amount": 1
            },
            "rewardPokemon": null,
            "endDate": "12 hours and 8 minutes"
        }
    ],
    "endDate": "12 hours and 8 minutes"
}
"""


class Missions(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.data = {}

    def set(self, missions):
        self.reset()
        for mission in missions["missions"]:
            if mission["progress"] >= mission["goal"]:
                continue
            try:
                mission_title = mission["name"].lower().replace("[flash]", " ").replace("é", "e").replace("wonder trade", "wondertrade").strip()
                mission_title = "".join([c for c in mission_title if c.isalnum() or c == " "]).strip()
                mission_title = " ".join([w for w in mission_title.split(" ") if w != ""])

                if "fish" in mission_title:
                    self.data["fish"] = True
                elif mission_title.startswith("wondertrade"):
                    if mission_title == "wondertrade":
                        # just wondertrade anything does not require a mission
                        pass
                    elif "bst" in mission_title:
                        the_bst = int("".join([c for c in mission_title if c.isnumeric()]))
                        if "less than" in mission_title:
                            self.data.setdefault("wondertrade_bst", []).append((0, the_bst))
                        else:
                            self.data.setdefault("wondertrade_bst", []).append((the_bst, 9999))
                    elif "kg" in mission_title:
                        pass
                    else:
                        the_type = mission_title.split(" ")[1].title()
                        self.data.setdefault("wondertrade_type", []).append(the_type)
                elif "miss" in mission_title and "catch" in mission_title:
                    self.data["miss"] = True
                elif mission_title == "attempt catches":
                    self.data["attempt"] = True
                elif mission_title.startswith("catch"):
                    if "kg" in mission_title:
                        the_kg = int("".join([c for c in mission_title.split("kg")[0] if c.isnumeric()]))
                        if "heavier than" in mission_title:
                            self.data.setdefault("weight", []).append((the_kg, 9999))
                        else:
                            self.data.setdefault("weight", []).append((0, the_kg))
                    elif "bst" in mission_title:
                        the_bst = int("".join([c for c in mission_title if c.isnumeric()]))
                        if "under" in mission_title or "less" in mission_title:
                            self.data.setdefault("bst", []).append((0, the_bst))
                        else:
                            self.data.setdefault("bst", []).append((the_bst, 9999))
                    else:
                        the_type = mission_title.split(" ")[1].title()
                        self.data.setdefault("type", []).append(the_type)
            except Exception as e:
                print(mission["name"], "parse fail", str(e))

    def have_mission(self, mission_name):
        return mission_name in self.data

    def _types_mission(self, mission_name, pokemon_types):
        if self.have_mission(mission_name):
            missions = self.data.get(mission_name)

            for pokemon_type in pokemon_types:
                if pokemon_type in missions:
                    return True

        return False

    def _between_mission(self, mission_name, unit):
        if self.have_mission(mission_name):
            missions = self.data.get(mission_name)

            for m_min, m_max in missions:
                if unit >= m_min and unit <= m_max:
                    return True

        return False

    # ##### Wondertrade Missions #####

    def check_wondertrade_type_mission(self, pokemon_types):
        return self._types_mission("wondertrade_type", pokemon_types)

    def check_wondertrade_bst_mission(self, bst):
        return self._between_mission("wondertrade_bst", bst)

    def check_all_wondertrade_missions(self, pokemon):
        reasons = []
        if self.check_wondertrade_type_mission(pokemon.types):
            reasons.append("type")

        if self.check_wondertrade_bst_mission(pokemon.bst):
            reasons.append("bst")
        return reasons

    def have_wondertrade_missions(self):
        if self.have_mission("wondertrade_type"):
            return True
        elif self.have_mission("wondertrade_bst"):
            return True
        return False

    # ##### Regular Missions #####

    def check_type_mission(self, pokemon_types):
        return self._types_mission("type", pokemon_types)

    def check_fish_mission(self):
        return self.have_mission("fish")

    def check_miss_mission(self):
        return self.have_mission("miss")

    def check_attempt_mission(self):
        return self.have_mission("attempt")

    def check_weight_mission(self, weight):
        return self._between_mission("weight", weight)

    def check_bst_mission(self, bst):
        return self._between_mission("bst", bst)

    def check_all_missions(self, pokemon):
        reasons = []
        if self.check_type_mission(pokemon.types):
            reasons.append("type")

        if self.check_weight_mission(pokemon.weight):
            reasons.append("weight")

        if self.check_bst_mission(pokemon.bst):
            reasons.append("bst")

        if pokemon.is_fish and self.check_fish_mission():
            reasons.append("fish")

        if self.check_miss_mission():
            reasons.append("miss")

        if self.check_attempt_mission():
            reasons.append("attempt")

        return reasons

    def mission_best_ball(self, mission):
        return mission not in ["attempt", "miss"]
