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


def get_sprite(sprite_type, sprite_name, shiny=False):
    check_output_folder(f"sprites/{sprite_type}")

    if sprite_type == "pokemon":
        extension = "gif"
    else:
        extension = "png"

    file_path = f"sprites/{sprite_type}/{sprite_name}.{extension}"

    if os.path.isfile(file_path):
        return open(file_path, "rb")

    if sprite_type == "pokemon":
        if shiny:
            url = f"https://dev.bframework.de/static/pokedex/sprites/front-shiny/{sprite_name}.gif"
        else:
            url = f"https://dev.bframework.de/static/pokedex/sprites/front/{sprite_name}.gif"

        res = requests.get(url)
        content = res.content
    else:
        get_png = True
        url = f"https://poketwitch.bframework.de/static/twitchextension/items/{sprite_type}/{sprite_name}"
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

    if sprite_type != "pokemon":
        im = Image.open(file_path)
        im = im.resize((32, 32))
        im.save(file_path)

    return open(file_path, "rb")
