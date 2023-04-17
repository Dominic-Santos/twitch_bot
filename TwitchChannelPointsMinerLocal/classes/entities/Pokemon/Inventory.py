CATCH_BALL_PRIORITY = ["ultraball", "greatball", "pokeball", "premierball"]
POKEMON_TYPES = ["Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy"]


class Inventory(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.cash = 0
        self.balls = {}
        self.items = []
        self.special_balls = {}

    def __str__(self):
        return "Balance: $" + str(self.cash) + " " + ", ".join(["{item}: {amount}".format(item=item["name"], amount=item["amount"]) for item in self.items])

    def set(self, inventory):
        self.reset()
        self.cash = inventory["cash"]
        for item in inventory["allItems"]:
            if item["category"] == "ball":
                ball = item["name"].lower().replace(" ", "")
                self.balls[ball] = item["amount"]

                for pokemon_type in POKEMON_TYPES:
                    if pokemon_type in item["description"]:
                        if pokemon_type not in self.special_balls:
                            self.special_balls[pokemon_type] = []
                        self.special_balls[pokemon_type].append(ball)

            else:
                self.items.append(item)

    def get_catch_ball(self, types=[], repeat=False, best=True):
        if best:
            return self.get_catch_best_ball(types, repeat)
        return self.get_catch_ball_worst()

    def get_catch_ball_worst(self):
        for item in CATCH_BALL_PRIORITY[::-1]:
            if self.have_ball(item):
                return item

    def get_catch_best_ball(self, types=[], repeat=False):
        if repeat:
            if self.have_ball("repeatball"):
                return "repeatball"

        if self.have_ball("ultraball"):
            return "ultraball"

        if types is not None:
            for t in sorted(types):
                if t in self.special_balls:
                    return self.special_balls[t][0]

        for item in CATCH_BALL_PRIORITY[1:]:
            if self.have_ball(item):
                return item

        return None

    def have_ball(self, ball):
        return self.balls.get(ball, 0) > 0
