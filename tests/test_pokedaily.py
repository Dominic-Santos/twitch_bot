from . import parse_message

TESTMSG = "You already have claimed your daily reward. Please come back in 5 hours, 25 minutes and 32 seconds."


def test_pokedaily():
    result = parse_message(TESTMSG)
    assert result.repeat
    assert result.valid
    assert result.rarity == "unknown"
    assert len(result.rewards) == 0
    # hours minutes seconds in message + last_redeemed should add up to 20h 0m 0s
    assert result.last_redeemed["hours"] == 14
    assert result.last_redeemed["minutes"] == 34
    assert result.last_redeemed["seconds"] == 28
