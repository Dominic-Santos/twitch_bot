"""
Todo:
    catch pokemon with X ball
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

                if mission_title.startswith("wondertrade"):
                    if mission_title == "wondertrade":
                        # just wondertrade anything does not require a mission
                        pass
                    elif "fish" in mission_title:
                        self.data["wondertrade_fish"] = True
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
                elif "fish" in mission_title:
                    self.data["fish"] = True
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

        if pokemon.is_fish and self.have_mission("wondertrade_fish"):
            reasons.append("fish")
        return reasons

    def have_wondertrade_missions(self):
        if self.have_mission("wondertrade_type"):
            return True
        elif self.have_mission("wondertrade_bst"):
            return True
        elif self.have_mission("wondertrade_fish"):
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
