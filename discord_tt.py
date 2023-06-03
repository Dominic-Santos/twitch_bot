import json


from TwitchChannelPointsMinerLocal.classes.entities.Pokemon.Discord import Discord
from TwitchChannelPointsMinerLocal.classes.entities.Pokemon.Utils import get_sprite

SETTINGS_FILE = "pokemon.json"
ALERTS_CHANNEL = 1072557550526013440
DISCORD_BASE = "https://discord.com/api/v9/"
DISCORD_ALERTS = f"{DISCORD_BASE}channels/{ALERTS_CHANNEL}/messages"


def load_settings():
    with open(SETTINGS_FILE, "r") as f:
        j = json.load(f)
        return j


def main():
    settings = load_settings()
    print(settings)
    discord = Discord()
    discord.set(settings["discord"])
    discord.connect()

    sprite = get_sprite("streamer", "theswedishfishofficial")

    print(sprite)

    the_file = ('./Untitled.png', sprite)
    # the_file2 = ('./Untitled.svg', bytesObj)
    # print(the_file)

    discord.post(DISCORD_ALERTS, "this will display rewards text here", file=the_file)
    # discord.post(DISCORD_ALERTS, "this worked2", file=None)


if __name__ == "__main__":
    main()
