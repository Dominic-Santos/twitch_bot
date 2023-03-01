from . import INVENTORY


def set_inventory(items={}, cash=100):
    INVENTORY.reset()
    INVENTORY.set_cash(cash)
    INVENTORY.set(items)


def test_inventory():
    items = {"pokeball": 10, "greatball": 11, "ultraball": 5}
    set_inventory(items)

    assert INVENTORY.get() == items
    assert INVENTORY.cash == 100
    for k in items.keys():
        assert INVENTORY.get_item(k) == items[k]


def test_basic_balls():
    items = {"pokeball": 1, "greatball": 1, "ultraball": 1, "premierball": 1}
    set_inventory(items)

    assert INVENTORY.get() == items
    for ball in ["ultraball", "greatball", "premierball", "pokeball", None]:
        assert ball == INVENTORY.get_catch_ball()
        INVENTORY.use(ball)


def test_repeat_balls():
    items = {"pokeball": 1, "greatball": 1, "ultraball": 1, "premierball": 1, "repeatball": 1}
    set_inventory(items)

    assert INVENTORY.get() == items

    for ball, repeat in [("ultraball", False), ("repeatball", True), ("greatball", True)]:
        assert ball == INVENTORY.get_catch_ball(repeat=repeat)
        INVENTORY.use(ball)


def test_special_balls():
    items = {"netball": 2, "nightball": 2, "phantomball": 2, "cipherball": 2, "frozenball": 2}
    set_inventory(items)

    assert INVENTORY.get() == items
    for poke_type, ball in [("Water", "netball"), ("Bug", "netball"), ("Dark", "nightball"), ("Ghost", "phantomball"), ("Poison", "cipherball"), ("Psychic", "cipherball"), ("Ice", "frozenball")]:
        assert ball == INVENTORY.get_catch_ball(types=[poke_type])
        INVENTORY.use(ball)
