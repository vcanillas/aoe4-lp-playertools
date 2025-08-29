from typing import Any, List

import requests

import settings

AOE4WORLD_URL_API = "https://aoe4world.com/api"


def search_players(text: str) -> dict[str, Any]:
    url = AOE4WORLD_URL_API + "/v0/players/search"
    params = {"query": text}

    # Make the GET request
    response = requests.get(url, params=params)

    # Check and print response
    if response.status_code == 200:
        return response.json()
    else:
        raise ("Error:", response.status_code, response.text)


def get_player(id: str):
    url = AOE4WORLD_URL_API + "/v0/players/" + id

    # Make the GET request
    response = requests.get(url)

    # Check and print response
    if response.status_code == 200:
        return response.json()
    else:
        raise ("Error:", response.status_code, response.text)


@staticmethod
def get_drafts(text: str) -> dict[str, Any]:
    url = AOE4WORLD_URL_API + "/v0/esports/drafts"
    params = {"preset": text, "api_key": settings.AOE4WORLD_API_KEY}

    # Make the GET request
    response = requests.get(url, params=params)

    # Check and print response
    if response.status_code == 200:
        return response.json()
    else:
        raise ("Error:", response.status_code, response.text)


def get_live_games(players_ids: List[int]):
    url = AOE4WORLD_URL_API + "/v0/games"
    params = {
        "state": "new",
        "leaderboard": "custom",
        "include_private": "true",
        "order": "updated_at",
        "page": 1,
        "profile_ids": ", ".join(str(id) for id in players_ids),
        "api_key": settings.AOE4WORLD_API_KEY,
    }

    # Make the GET request
    response = requests.get(url, params=params)

    # Check and print response
    if response.status_code == 200:
        return response.json()
    else:
        raise ("Error:", response.status_code, response.text)
