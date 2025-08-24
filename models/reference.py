from repositories.json_repository import JsonRepository
from repositories.pickle_repository import PickleRepository
import settings


CIVILIZATIONS = {
    "eng": {"relic": 106553, "aoe4world": "english"},
    "mon": {"relic": 129267, "aoe4world": "mongols"},
    "fre": {"relic": 131384, "aoe4world": "french"},
    "rus": {"relic": 133008, "aoe4world": "rus"},
    "hre": {"relic": 134522, "aoe4world": "holy_roman_empire"},
    "del": {"relic": 136150, "aoe4world": "delhi_sultanate"},
    "chi": {"relic": 137266, "aoe4world": "chinese"},
    "abb": {"relic": 199703, "aoe4world": "abbasid_dynasty"},
    "ott": {"relic": 2039321, "aoe4world": "ottomans"},
    "mal": {"relic": 2058393, "aoe4world": "malians"},
    "byz": {"relic": 2101234, "aoe4world": "byzantines"},
    "jap": {"relic": 2109886, "aoe4world": "japanese"},
    "jea": {"relic": 2121948, "aoe4world": "jeanne_darc"},
    "ayy": {"relic": 2121949, "aoe4world": "ayyubids"},
    "zhu": {"relic": 2121950, "aoe4world": "zhu_xis_legacy"},
    "ord": {"relic": 2121952, "aoe4world": "order_of_the_dragon"},
    "knt": {"relic": 5000002, "aoe4world": "knights_templar"},
    "hol": {"relic": 5000003, "aoe4world": "house_of_lancaster"},
    "mac": {"relic": 1, "aoe4world": "mac"},
    "goh": {"relic": 2, "aoe4world": "goh"},
    "sen": {"relic": 3, "aoe4world": "sen"},
    "tug": {"relic": 4, "aoe4world": "tug"},
}


def get_Players() -> dict[int, str]:
    data = PickleRepository.load_data("players.pkl")

    if settings.DEBUG:
        JsonRepository.save_data("players.json", data)

    # Convert keys from string to int
    int_keys_data = {int(k): v for k, v in data.items()}
    return int_keys_data


def get_Maps() -> dict[str, str]:
    return JsonRepository.load_data("maps.json")


def get_Draft() -> dict[str, str]:
    return JsonRepository.load_data("draft.json")
