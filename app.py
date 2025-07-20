import requests, json
from typing import List
from flask import Flask, request, jsonify, render_template
from reference import PLAYERS
import model, settings

app = Flask(__name__)


def mock():
    # Mock response data, typically loaded from a.json
    with open("./flux/flux-None.json", "r", encoding="utf-8") as f:
        return json.load(f)


def call(url, params) -> str:
    # Make the GET request
    response = requests.get(url, params=params)

    # Check and print response
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)


def process_data(data, player1_id) -> List[model.Map]:
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
                player.alias = profile.get("alias", "")
                player.set_lp_name()
                player.set_civilization_id(member.get("civilization_id"))

            team_id = member.get("teamid")

            # Find team
            team = next((team for team in match.teams if team.team_id == team_id), None)
            if team is None:
                team = model.Team()
                team.team_id = team_id
                team.result_type = result.get("resulttype")
                match.teams.append(team)

            team.players.append(player)

        # Set Summary at the end
        if match.set_final(player1_id):
            matches.append(match)

    return matches


def get_all_players(matches: List[model.Map]):
    # Make a shallow copy of PLAYERS to avoid modifying the original list
    updated_players = PLAYERS.copy()

    for match in matches:
        for team in match.teams:
            for player in team.players:
                player_id = player.profile_id
                # If player not already in PLAYERS
                if player.profile_id not in updated_players:
                    # Create new player object
                    updated_players[player.profile_id] = player.alias

    return updated_players


@app.route("/get_players", methods=["GET"])
def get_players():
    return jsonify(PLAYERS)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/games", methods=["POST"])
def map_route():

    data = request.get_json()
    player_id = int(data.get("player_id"))

    player2 = data.get("player_id2")
    if player2 is not None and player2 != "":
        player_id = int(player2)

    # Your API URL with parameters
    url = settings.URL_API
    params = {"title": "age4", "profile_ids": json.dumps([player_id])}

    # Call & save result (for cache)
    if settings.USE_MOCK:
        api_result = mock()
        player_id = 1
    else:
        api_result = call(url, params)

    maps = process_data(api_result, player_id)

    map_dicts = [item.to_dict() for item in maps]

    if settings.DEBUG:
        with open(f"./flux/flux-{player_id}.json", "w") as json_file:
            json.dump(api_result, json_file, indent=2)

        print(map_dicts)

        with open("./flux/result.json", "w") as json_file:
            json.dump(map_dicts, json_file, indent=2)

    all_players = get_all_players(maps)

    return jsonify({"players": all_players, "maps": map_dicts})


if __name__ == "__main__":
    app.run(debug=True)
