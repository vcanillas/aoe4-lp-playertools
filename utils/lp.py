from reference import CIVILIZATIONS, get_Maps, get_Players


@staticmethod
def get_civilization_lp(id):
    try:
        return CIVILIZATIONS.get(id, f"### Unknown - {id}")
    except KeyError:
        return f"Unknow_Key ### - {id}"


@staticmethod
def get_map_lp(id, label):
    try:
        return get_Maps().get(id, f"### Unknown - {id} - {label}")
    except KeyError:
        return f"Unknow_Key ### - {id} - {label}"


@staticmethod
def get_player_name_lp(id, label):
    try:
        return get_Players().get(id, f"{label} - ### Unknown - {id}")
    except KeyError:
        return f"Unknow_Key ### - {id} - {label} - "


def get_participants(data, with_flag=False):
    entries = data["data"]["event"]["standings"]["nodes"]

    result = ""
    for idx, node in enumerate(entries, start=1):
        name = node["entrant"]["name"]
        line = f"|p{idx}={name}"
        if with_flag:
            flag = node["entrant"]["participants"][0]["user"]["location"]["country"]
            line += f" |p{idx}flag={flag}"
        result += line + "<br />"

    return result
