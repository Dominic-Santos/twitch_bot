from . import MISSIONS


def test_type_mission():
    type_mission, type_target, type_caught = MISSIONS.get_type_mission()

    assert type_mission is None
    assert isinstance(type_target, int)
    assert isinstance(type_caught, int)

    test_case = {
        "type_mission": "Fire",
        "type_target": 1,
        "type_caught": 0,
    }

    MISSIONS.set(test_case)

    assert MISSIONS.check_type_mission([]) is False
    assert MISSIONS.check_type_mission([], inc=True) is False
    assert MISSIONS.check_type_mission([test_case["type_mission"]])
    assert MISSIONS.check_type_mission([test_case["type_mission"]], inc=True)
    assert MISSIONS.check_type_mission([test_case["type_mission"]]) is False
    assert MISSIONS.check_type_mission([test_case["type_mission"]], inc=True) is False

    msg, best = MISSIONS.mission_message("type")
    assert msg == f"is {test_case['type_mission']} type"
    assert best == True


def test_miss_mission():
    miss_target = MISSIONS.data["miss_target"]
    miss_caught = MISSIONS.data["miss_caught"]

    assert isinstance(miss_target, int)
    assert isinstance(miss_caught, int)

    test_case = {
        "miss_target": 1,
        "miss_caught": 0,
    }

    MISSIONS.set(test_case)

    assert MISSIONS.check_miss_mission()
    assert MISSIONS.check_miss_mission(inc=True)
    assert MISSIONS.check_miss_mission() is False
    assert MISSIONS.check_miss_mission(inc=True) is False

    msg, best = MISSIONS.mission_message("miss")
    assert msg == "need to miss more pokemon"
    assert best == False


def test_attempt_mission():
    attempt_target = MISSIONS.data["attempt_target"]
    attempt_caught = MISSIONS.data["attempt_caught"]

    assert isinstance(attempt_target, int)
    assert isinstance(attempt_caught, int)

    test_case = {
        "attempt_target": 1,
        "attempt_caught": 0,
    }

    MISSIONS.set(test_case)

    assert MISSIONS.check_attempt_mission()
    assert MISSIONS.check_attempt_mission(inc=True)
    assert MISSIONS.check_attempt_mission() is False
    assert MISSIONS.check_attempt_mission(inc=True) is False

    msg, best = MISSIONS.mission_message("attempt")
    assert msg == "need to attempt more pokemon"
    assert best == False


def test_weight_mission():
    weight_target = MISSIONS.data["weight_target"]
    weight_caught = MISSIONS.data["weight_caught"]
    weight_min = MISSIONS.data["weight_min"]
    weight_max = MISSIONS.data["weight_max"]

    assert isinstance(weight_target, int)
    assert isinstance(weight_caught, int)
    assert isinstance(weight_min, int)
    assert isinstance(weight_max, int)

    test_case = {
        "weight_target": 1,
        "weight_caught": 0,
        "weight_min": 100,
        "weight_max": 200,
    }

    MISSIONS.set(test_case)

    assert MISSIONS.check_weight_mission(10) is False
    assert MISSIONS.check_weight_mission(300, inc=True) is False
    assert MISSIONS.check_weight_mission(150)
    assert MISSIONS.check_weight_mission(150, inc=True)
    assert MISSIONS.check_weight_mission(150) is False
    assert MISSIONS.check_weight_mission(150, inc=True) is False

    msg, best = MISSIONS.mission_message("weight")
    assert msg == f"is between {test_case['weight_min']} and {test_case['weight_max']} KG"
    assert best == True


def test_bst_mission():
    bst_target = MISSIONS.data["bst_target"]
    bst_caught = MISSIONS.data["bst_caught"]
    bst_min = MISSIONS.data["bst_min"]
    bst_max = MISSIONS.data["bst_max"]

    assert isinstance(bst_target, int)
    assert isinstance(bst_caught, int)
    assert isinstance(bst_min, int)
    assert isinstance(bst_max, int)

    test_case = {
        "bst_target": 1,
        "bst_caught": 0,
        "bst_min": 100,
        "bst_max": 600,
    }

    MISSIONS.set(test_case)

    assert MISSIONS.check_bst_mission(10) is False
    assert MISSIONS.check_bst_mission(700, inc=True) is False
    assert MISSIONS.check_bst_mission(150)
    assert MISSIONS.check_bst_mission(150, inc=True)
    assert MISSIONS.check_bst_mission(150) is False
    assert MISSIONS.check_bst_mission(150, inc=True) is False

    msg, best = MISSIONS.mission_message("bst")
    assert msg == f"is between {test_case['bst_min']} and {test_case['bst_max']} bst"
    assert best == True
