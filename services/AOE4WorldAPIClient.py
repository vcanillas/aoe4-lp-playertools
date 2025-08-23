from typing import Any

import requests

import reference, settings

AOE4WORLD_URL_API = "https://aoe4world.com/api"


@staticmethod
def search_players(text: str) -> dict[str, Any]:
    url = AOE4WORLD_URL_API + "/v0/players/search"
    params = {"query": text}

    # Make the GET request
    response = requests.get(url, params=params)

    # Check and print response
    if response.status_code == 200:
        api_result = response.json()
    else:
        raise ("Error:", response.status_code, response.text)

    lp_players = reference.get_Players()

    result = []
    for player in api_result["players"]:
        result_player = {
            "name": player.get("name"),
            "profile_id": player.get("profile_id"),
            "country": player.get("country"),
            "steam_id": player.get("steam_id"),
            "lp_name": lp_players.get(player.get("profile_id"), ""),
        }
        result.append(result_player)

    return result


@staticmethod
def get_drafts(text: str) -> dict[str, Any]:
    url = AOE4WORLD_URL_API + "/v0/esports/drafts"
    params = {"preset": text, "api_key": settings.AOE4WORLD_API_KEY}

    # Make the GET request
    response = requests.get(url, params=params)

    # Check and print response
    if response.status_code == 200:
        api_result = response.json()
    else:
        raise ("Error:", response.status_code, response.text)

    result = []
    for draft in api_result["drafts"]:
        drafts = {
            "draft": "http://aoe2cm.net/draft/" + draft.get("draft"),
            "draft_name": draft.get("preset_name"),
            "player_1": draft.get("host_name"),
            "player_2": draft.get("guest_name"),
            "date": draft.get("created_at"),
        }
        result.append(drafts)

    return result
