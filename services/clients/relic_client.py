import json
from typing import List

import requests

import settings

RELIC_URL_API = "https://aoe-api.worldsedgelink.com"


def get_recent_match_history(players_ids: List[int]):

    def mock():
        # Mock response data, typically loaded from .json
        with open("./flux/flux-None.json", "r", encoding="utf-8") as f:
            return json.load(f)

    # Your API URL with parameters
    url = RELIC_URL_API + "/community/leaderboard/getRecentMatchHistory"
    params = {"title": "age4", "profile_ids": json.dumps(players_ids)}

    # Call & save result (for cache)
    if settings.USE_MOCK:
        return mock()
    else:
        # Make the GET request
        response = requests.get(url, params=params)

        # Check and print response
        if response.status_code == 200:
            return response.json()
        else:
            raise ("Error:", response.status_code, response.text)
