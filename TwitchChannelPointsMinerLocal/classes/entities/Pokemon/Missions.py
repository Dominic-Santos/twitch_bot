"""
Todo:
    catch pokemon by weight (heavier, lighter, between?)
    catch pokemon with X ball
    confirm attemp message
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

            mission_title = mission["name"].lower().replace("[flash]", " ").strip()
            mission_title = "".join([c for c in mission_title if c.isalnum() or c == " "]).strip()
            mission_title = " ".join([w for w in mission_title.split(" ") if w != ""])

            if mission_title.startswith("wondertrade") and mission_title.endswith("types"):
                the_type = mission_title.split(" ")[1].title()
                self.data.setdefault("wondertrade", []).append(the_type)
            elif mission_title == "miss catches":
                self.data["miss"] = True
            elif mission_title == "attempt catches":
                self.data["attemp"] = True
            elif mission_title.startswith("catch") and "type pokemon" in mission_title:
                the_type = mission_title.split(" ")[1].title()
                self.data.setdefault("type", []).append(the_type)

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

    def check_type_mission(self, pokemon_types):
        return self._types_mission("type", pokemon_types)

    def check_wondertrade_mission(self, pokemon_types):
        return self._types_mission("wondertrade", pokemon_types)

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

        if self.check_miss_mission():
            reasons.append("miss")

        if self.check_attempt_mission():
            reasons.append("attempt")

        return reasons

    def mission_best_ball(self, mission):
        return mission not in ["attempt", "miss"]
