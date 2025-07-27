import json
import os

CIVILIZATIONS = {
    106553: "eng",
    129267: "mon",
    131384: "fre",
    133008: "rus",
    134522: "hre",
    136150: "del",
    137266: "chi",
    199703: "abb",
    2039321: "ott",
    2058393: "mal",
    2101234: "byz",
    2109886: "jap",
    2121948: "jea",
    2121949: "ayy",
    2121950: "zhu",
    2121952: "ord",
    5000002: "knt",
    5000003: "hol",
}


def get_Players():
    data = load_data("players.json")
    # Convert keys from string to int
    int_keys_data = {int(k): v for k, v in data.items()}
    return int_keys_data


def get_Maps():
    return load_data("maps.json")


@staticmethod
def load_data(filename):
    with open(os.path.join(os.path.dirname(__file__), "data", filename), "r") as f:
        return json.load(f)


@staticmethod
def save_data(filename, data):
    with open(os.path.join(os.path.dirname(__file__), "data", filename), "w") as f:
        json.dump(data, f, indent=4)

# Sort the list by the 'name' key
# sorted_items = sorted(MAPS.items(), key=lambda item: item[0].lower())

# # Print the sorted list
# for key, name in sorted_items:
#     print(f"'{key}': '{name}',")
