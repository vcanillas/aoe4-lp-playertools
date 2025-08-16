import json
from typing import List

import requests
import model, settings

RELIC_URL_API = "https://aoe-api.worldsedgelink.com"


def get_recent_match(players_ids: List[int]) -> List[model.Map]:

    def mock():
        # Mock response data, typically loaded from a.json
        with open("./flux/flux-None.json", "r", encoding="utf-8") as f:
            return json.load(f)

    # Your API URL with parameters
    url = RELIC_URL_API + "/community/leaderboard/getRecentMatchHistory"
    params = {"title": "age4", "profile_ids": json.dumps(players_ids)}

    # Call & save result (for cache)
    if settings.USE_MOCK:
        api_result = mock()
        players_ids = 11628131
    else:
        # Make the GET request
        response = requests.get(url, params=params)

        # Check and print response
        if response.status_code == 200:
            api_result = response.json()
        else:
            raise ("Error:", response.status_code, response.text)

    maps = _process_data(api_result, players_ids)

    if settings.DEBUG:
        with open(f"./flux/flux-{players_ids}.json", "w") as json_file:
            json.dump(api_result, json_file, indent=2)

        map_dicts = [item.to_dict() for item in maps]

        with open("./flux/result.json", "w") as json_file:
            json.dump(map_dicts, json_file, indent=2)

    return maps


def _process_data(data, player1_id) -> List[model.Map]:
    matches = []

    # Extract match history
    matchHistoryStats = data.get("matchHistoryStats")

    # Filter matches
    matchHistoryStats = [
        match for match in matchHistoryStats if match.get("matchtype_id") == 0
    ]
    # Sort matches by 'matchstartdate' descending
    matchHistoryStats = sorted(
        matchHistoryStats, key=lambda x: x["startgametime"], reverse=True
    )

    # TemporaryCode - limit
    # matchHistoryStats = [matchHistoryStats[0]]

    for matchHistoryStat in matchHistoryStats:
        match = model.Map()
        match.matchtype_id = matchHistoryStat.get("id")
        match.set_start_game_time(matchHistoryStat.get("startgametime"))
        match.completion_time = matchHistoryStat.get("completiontime")
        match.set_option_raw(matchHistoryStat.get("options"))

        # Loop through matchhistorymember to assign players to teams
        for member in matchHistoryStat.get("matchhistorymember", []):
            profile_id = member["profile_id"]

            profile = next(
                (
                    profile
                    for profile in data["profiles"]
                    if profile.get("profile_id") == profile_id
                ),
                None,
            )
            result = next(
                (
                    mhrr
                    for mhrr in matchHistoryStat["matchhistoryreportresults"]
                    if mhrr.get("profile_id") == profile_id
                ),
                None,
            )

            player = model.Player()
            player.profile_id = profile_id

            if profile is not None:
                player.name_raw = profile.get("alias", "")
                player.set_lp_name()
                player.set_civilization_id(member.get("civilization_id"))

            team_id = result.get("resulttype")  # Team_id based on resulttype

            # Find team
            team = next((team for team in match.teams if team.team_id == team_id), None)
            if team is None:
                team = model.Team()
                team.team_id = team_id
                team.result_type = result.get("resulttype")
                match.teams.append(team)

            team.players.append(player)

        # Set Summary at the end
        if match.complete_data(player1_id):
            matches.append(match)

    return matches
