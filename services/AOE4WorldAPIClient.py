from typing import Any

import requests

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

    result = []
    for player in api_result["players"]:
        result_player = {
            "name": player.get("name"),
            "profile_id": player.get("profile_id"),
            "country": player.get("country"),
            "steam_id": player.get("steam_id"),
        }
        result.append(result_player)

    return result
