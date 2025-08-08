from utils.static import load_data


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


def get_Players() -> dict[int, str]:
    data = load_data("players.json")
    # Convert keys from string to int
    int_keys_data = {int(k): v for k, v in data.items()}
    return int_keys_data


def get_Maps() -> dict[str, str]:
    return load_data("maps.json")
