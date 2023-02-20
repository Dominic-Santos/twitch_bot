class Missions(object):
    def __init__(self):
        self.data = {
            "type_mission": None,
            "type_target": 0,
            "type_caught": 0,
            "missed_target": 0,
            "missed_caught": 0,
            "weight_min": 0,
            "weight_max": 0,
            "weight_target": 0,
            "weight_caught": 0,
        }
        self.discord = None
        self.last_type = []

    def set(self, data):
        for key in data:
            if key in self.data:
                self.data[key] = data[key]

    def set_pokedex(self, pokedex):
        self.pokedex = pokedex

    def get_missed_mission(self):
        t = self.data.get("missed_target")
        c = self.data.get("missed_caught")
        return t, c

    def check_missed_mission(self, inc=False):
        target, caught = self.get_missed_mission
        catch = caught < target

        if catch and inc:
            self.data["missed_caught"] = caught + 1

        return catch

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

    def get_weight_mission(self):
        _min = self.data.get("weight_min")
        _max = self.data.get("weight_max")
        t = self.data.get("weight_target")
        c = self.data.get("weight_caught")
        return (_min, _max), t, c

    def check_weight_mission(self, inc=False):
        limits, target, caught = self.get_weight_mission()
        weight = self.pokedex.get_weight()

        # limits = (min, max)
        catch = weight >= limits[0] and weight <= limits[1]

        if catch and inc:
            self.data["weight_caught"] = caught + 1

        return catch
