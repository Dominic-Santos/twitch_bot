class Missions(object):
    def __init__(self):
        self.data = {
            "type_mission": None,
            "type_target": 0,
            "type_caught": 0,

            "miss_target": 0,
            "miss_caught": 0,

            "attempt_target": 0,
            "attempt_caught": 0,

            "weight_min": 0,
            "weight_max": 0,
            "weight_target": 0,
            "weight_caught": 0,

            "bst_min": 0,
            "bst_max": 0,
            "bst_target": 0,
            "bst_caught": 0,
        }
        self.discord = None
        self.last_type = []

    def set(self, data):
        for key in data:
            if key in self.data:
                self.data[key] = data[key]

    def counter_mission(self, prefix, inc=False):
        target = self.data.get(f"{prefix}_target")
        caught = self.data.get(f"{prefix}_caught")
        catch = caught < target

        if catch and inc:
            self.data[f"{prefix}_caught"] = caught + 1

        return catch

    def check_miss_mission(self, inc=False):
        return self.counter_mission("miss", inc)

    def check_attempt_mission(self, inc=False):
        return self.counter_mission("attempt", inc)

    def get_type_mission(self):
        m = self.data.get("type_mission")
        t = self.data.get("type_target")
        c = self.data.get("type_caught")
        return m, t, c

    def check_type_mission(self, pokemon_types, inc=False):
        mission, target, caught = self.get_type_mission()
        catch = False

        if mission in pokemon_types:
            catch = caught < target

        if catch and inc:
            self.data["type_caught"] = caught + 1

        return catch

    def between_mission(self, prefix, unit, inc=False):
        limit_min = self.data.get(f"{prefix}_min")
        limit_max = self.data.get(f"{prefix}_max")
        target = self.data.get(f"{prefix}_target")
        caught = self.data.get(f"{prefix}_caught")

        catch = unit >= limit_min and unit <= limit_max and caught < target

        if catch and inc:
            self.data[f"{prefix}_caught"] = caught + 1

        return catch

    def check_weight_mission(self, weight, inc=False):
        return self.between_mission("weight", weight, inc)

    def check_bst_mission(self, bst, inc=False):
        return self.between_mission("bst", bst, inc)

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

    def check_missions_increment(self, pokemon, caught=True):
        if caught:
            self.check_bst_mission(pokemon.bst, inc=True)
            self.check_weight_mission(pokemon.weight, inc=True)
            self.check_type_mission(pokemon.types, inc=True)
        else:
            self.check_miss_mission(inc=True)

        self.check_attempt_mission(inc=True)

    def mission_best_ball(self, mission):
        return mission not in ["attempt", "miss"]

    def mission_message(self, mission):
        if mission == "type":
            m = self.data["type_mission"]
            mission_msg = f"is {m} type"
        elif mission in ["bst", "weight"]:
            m_min = self.data[f"{mission}_min"]
            m_max = self.data[f"{mission}_max"]
            m_unit = {"bst": "bst", "weight": "KG"}
            mission_msg = f"is between {m_min} and {m_max} {m_unit[mission]}"
        elif mission in ["attempt", "miss"]:
            mission_msg = f"need to {mission} more pokemon"
        else:
            mission_msg = f"{mission} mission"

        return mission_msg
