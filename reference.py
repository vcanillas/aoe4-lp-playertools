import settings
from utils.static import load_data_json, load_data_pickle, save_data_json


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
    1: "mac",
    2: "goh",
    3: "sen",
    4: "tug",
}


def get_Players() -> dict[int, str]:
    data = load_data_pickle("players.pkl")

    if settings.DEBUG:
        save_data_json("players.json", data)

    # Convert keys from string to int
    int_keys_data = {int(k): v for k, v in data.items()}
    return int_keys_data


def get_Maps() -> dict[str, str]:
    return load_data_json("maps.json")


def get_Draft() -> dict[str, str]:
    return load_data_json("draft.json")
