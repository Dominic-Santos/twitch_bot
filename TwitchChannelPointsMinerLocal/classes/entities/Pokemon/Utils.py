import os
import json


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
