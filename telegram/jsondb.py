import os
import json


def init():
    if not os.path.exists("settings.json"):
        data = {
            "use_unic_on_links": True,
        }

        with open("settings.json", "w") as json_file:
            json.dump(data, json_file, indent=4)


def get_use_unic_on_links():
    with open("settings.json", "r") as json_file:
        data = json.load(json_file)
    return data["use_unic_on_links"]


def toggle_use_unic_on_links():
    with open("settings.json", "r") as json_file:
        data = json.load(json_file)

    data["use_unic_on_links"] = not data["use_unic_on_links"]

    with open("settings.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
