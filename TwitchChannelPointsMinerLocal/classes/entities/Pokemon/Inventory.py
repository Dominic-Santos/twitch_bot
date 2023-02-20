CATCH_BALL_PRIORITY = ["ultraball", "greatball", "premierball", "pokeball"]
CATCH_SPECIAL_BALLS = {
    "Water": "netball",
    "Bug": "netball",
    "Dark": "nightball",
    "Ghost": "phantomball",
    "Poison": "cipherball",
    "Psychic": "cipherball",
    "Ice": "frozenball"
}


class Inventory(object):
    def __init__(self):
        self.reset()
        self.last_used = None

    def __str__(self):
        return "Balance: $" + str(self.cash) + " " + ", ".join(["{item}: {amount}".format(item=item, amount=self.get_item(item)) for item in sorted(self.items.keys())])

    def get(self):
        return self.items

    def set(self, items):
        self.items = items

    def reset(self):
        self.items = {}
        self.cash = 0

    def add_item(self, item, amount):
        self.items[item] = self.get_item(item) + amount

    def remove_item(self, item, amount):
        self.items[item] = self.get_item(item) - amount

    def get_item(self, item):
        return self.items.get(item, 0)

    def set_item(self, item, amount):
        self.items[item] = amount

    def have_item(self, item):
        return self.get_item(item) > 0

    def use(self, item):
        if self.have_item(item):
            self.remove_item(item, 1)
            self.last_used = item

    def set_cash(self, cash):
        self.cash = cash

    def get_catch_ball(self, types=[], repeat=False, best=True):
        if best:
            return self.get_catch_best_ball(types, repeat)
        return self.get_catch_ball_worst()

    def get_catch_ball_worst(self):
        for item in CATCH_BALL_PRIORITY[::-1]:
            if self.have_item(item):
                return item

    def get_catch_best_ball(self, types=[], repeat=False):
        if repeat:
            if self.have_item("repeatball"):
                return "repeatball"

        if types is not None:
            for t in sorted(types):
                if t in CATCH_SPECIAL_BALLS:
                    if self.have_item(CATCH_SPECIAL_BALLS[t]):
                        return CATCH_SPECIAL_BALLS[t]

        for item in CATCH_BALL_PRIORITY:
            if self.have_item(item):
                return item

        return None
