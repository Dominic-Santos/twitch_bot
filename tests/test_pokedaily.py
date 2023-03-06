from . import parse_message

TESTMSG = "You already have claimed your daily reward. Please come back in 5 hours, 25 minutes and 32 seconds."
TESTMSG2 = """You already have claimed your daily reward. Please come back in 13 hours, 54 minutes and 5 seconds.

Your last reward:

This is the Tentacool of the rewards, absolutely common:
:rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common:
:rarity_common: $10
:rarity_common: 2x Premier Ball
:rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common:"""


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
