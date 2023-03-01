
class Pokemon(object):
    def __init__(self):
        self.name = "NA"
        self.bst = 0
        self.weight = 0
        self.pokemon_id = 0
        self.tier = "NA"
        self.types = []
        self.spawn = None

        self.is_alternate = False
        self.alt_name = "NA"

    @property
    def pokedex_name(self):
        if self.name.startswith("Aegislash"):
            return "Aegislash (Shield)"
        return self.name.split("(")[0].strip()

    def check_name(self):
        if self.name.startswith("Rotom"):
            self.name = self.name.replace(" ", " (") + ")"

    def __str__(self):
        alt_name = "" if self.is_alternate is False else f" ({self.pokemon_id} - {self.alt_name})"
        return f"{self.spawn} {self.name}{alt_name}, {self.bst}BST, {self.weight}KG, tier {self.tier}, types {self.types}"
