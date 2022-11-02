import random
import json
from datetime import datetime

CATCH_TRIGGER = 2
CATCH_DELAY = 90  # seconds
CATCH_BALL_PRIORITY = ["ultraball", "premierball", "pokeball"]

INVENTORY_FILE = "inventory.json"
BALANCE_TRIGGER = 2
ITEM_MIN_AMOUNT = 30
ITEM_MIN_PURCHASE = 10
ITEM_PRIORITY = ["pokeball", "ultraball"]
ITEM_PRICES = {
    "pokeball": 300,
    "ultraball": 1000,
}


class PokemonComunityGame(object):
    def __init__(self):
        self.connected = False
        self.twitch = None
        self.channel_list = []

        self.catch_counter = 0
        self.catch_timer = datetime.now()

        self.check_balance_counter = 0

        self.last_catch = None
        self.last_channel = None

        self.inventory = {}
        self.cash = 0

        self.load_inventory()

    def save_inventory(self):
        with open(INVENTORY_FILE, "w") as f:
            f.write(json.dumps(self.inventory, indent=4))

    def load_inventory(self):
        try:
            with open(INVENTORY_FILE, "r") as f:
                self.inventory = json.load(f)
        except:
            self.inventory = {}

    def set_cash(self, cash):
        self.cash = cash

    def add_channel(self, channel):
        if channel not in self.channel_list:
            self.channel_list.append(channel)

    def remove_channel(self, channel):
        if channel in self.channel_list:
            self.channel_list.remove(channel)

    def random_channel(self):
        if len(self.channel_list) == 0:
            return None
        return random.choice(self.channel_list)

    def check_catch(self):
        now = datetime.now()
        if (now - self.catch_timer).total_seconds() > CATCH_DELAY:
            self.catch_timer = now
            self.catch_counter = 0

        self.catch_counter += 1

        if self.catch_counter == CATCH_TRIGGER:
            return True

        return False

    def last_attempt(self, set_to=None, channel=None):
        if set_to is None:
            return self.last_catch, self.last_channel

        self.last_catch = set_to
        self.last_channel = channel

    def add_item(self, item, amount):
        if item in self.inventory:
            self.inventory[item] = self.inventory[item] + amount
        else:
            self.inventory[item] = amount

    def get_item(self, item):
        if item in self.inventory:
            return self.inventory[item]
        return 0

    def get_catch_message(self, use=True):
        for item in CATCH_BALL_PRIORITY:
            have = self.get_item(item)
            if have > 0:
                if use:
                    self.inventory[item] = self.inventory[item] - 1
                return f"!pokecatch {item}"
        return "!pokecatch"

    def check_balance(self):
        self.check_balance_counter += 1

        if self.check_balance_counter == BALANCE_TRIGGER:
            self.check_balance_counter = 0
            return True

        return False

    def get_purchase_list(self, buy=False):
        cash = self.cash + 0
        purchases = []

        for item in ITEM_PRIORITY:
            have = self.get_item(item)
            if have < ITEM_MIN_AMOUNT:
                price = ITEM_PRICES[item] * ITEM_MIN_PURCHASE
                if price > cash:
                    break

                amount = cash // price
                purchases.append((item, amount * ITEM_MIN_PURCHASE))
                cash = cash % price

        if buy:
            self.cash = cash

        return purchases

    def get_inventory(self):
        return "Balance: $" + str(self.cash) + " " + ", ".join(["{item}: {amount}".format(item=item, amount=self.inventory[item]) for item in sorted(self.inventory.keys())])
