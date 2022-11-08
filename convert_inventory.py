import json

OLD_FILE = "inventory.json"
NEW_FILE = "pokemon.json"


def convert():
    inventory = {}
    settings = {}

    try:
        with open(OLD_FILE, "r") as f:
            inventory = json.load(f)
    except:
        print("could not process", OLD_FILE)

    with open(NEW_FILE, "w") as f:
        f.write(json.dumps({
            "inventory": inventory,
            "settings": settings
        }, indent=4))


if __name__ == "__main__":
    convert()
