import os
import json
import base64
import requests
from bs4 import BeautifulSoup
from PIL import Image


def check_output_folder(folder):
    if os.path.exists(folder) is False:
        os.makedirs(folder)


def save_to_file(filename, data):
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))


def save_to_json(func):
    def wrapped(obj, *args, **kwargs):
        obj_name = obj.__class__.__name__
        func_name = func.__name__

        result = func(obj, *args, **kwargs)

        check_output_folder(f"results/{obj_name}")
        save_to_file(f"results/{obj_name}/{func_name}.json", result)

        return result
    return wrapped


def get_sprite(sprite_type, sprite_name):
    check_output_folder(f"sprites/{sprite_type}")

    file_path = f"sprites/{sprite_type}/{sprite_name}.png"

    if os.path.isfile(file_path):
        return open(file_path, "rb")

    get_png = True

    if sprite_type == "pokemon":
        url = f"https://poketwitch.bframework.de/static/pokedex/png-sprites/pokemon/{sprite_name}.png"
        size = 128
    else:
        url = f"https://poketwitch.bframework.de/static/twitchextension/items/{sprite_type}/{sprite_name}"
        size = 32
        try:
            res = requests.get(url + ".svg")
            soup = BeautifulSoup(res.text, "html.parser")
            svg = soup.find("image")

            href = svg["href"]

            s = href.split("base64,")[1]

            img_data = s.encode()
            content = base64.b64decode(img_data)
            get_png = False
        except:
            url = url + ".png"

    if get_png:
        res = requests.get(url)
        content = res.content

        if res.status_code != 200:
            return None

    with open(file_path, "wb") as o:
        o.write(content)

    im = Image.open(file_path)
    im = im.resize((size, size))
    im.save(file_path)

    return open(file_path, "rb")
