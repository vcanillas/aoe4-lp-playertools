import json

from typing import List
from flask import Flask, request, jsonify, render_template
import reference, static, model, settings

app = Flask(__name__)


def mock():
    # Mock response data, typically loaded from a.json
    with open("./flux/flux-None.json", "r", encoding="utf-8") as f:
        return json.load(f)


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


def get_all_players(matches: List[model.Map]):
    # Make a shallow copy of PLAYERS to avoid modifying the original list
    updated_players = reference.get_Players().copy()

    for match in matches:
        for team in match.teams:
            for player in team.players:
                # If player not already in players
                if player.profile_id not in updated_players:
                    # Create new player object
                    updated_players[player.profile_id] = player.alias

    return updated_players


@app.route("/players", methods=["GET"])
def get_players():
    return reference.get_Players()


@app.route("/player", methods=["POST"])
def add_player():
    players = reference.get_Players()
    new_id = request.json.get("id")
    new_value = request.json.get("value")
    if new_id in players:
        return jsonify({"error": "ID already exists"}), 400
    players[new_id] = new_value

    sorted_maps = dict(sorted(players.items(), key=lambda item: item[1]))
    reference.save_data("players.json", sorted_maps)
    return jsonify({"message": "Player added"}), 201


@app.route("/search_player", methods=["POST"])
def search_player():
    text = request.json.get("text")
    url = settings.AOE4WORLD_URL_API
    params = {"query": text}
    api_result = static.call(url, params)

    result = []
    for player in api_result["players"]:
        result_player = {
            "name": player.get("name"),
            "profile_id": player.get("profile_id"),
            "country": player.get("country"),
        }
        result.append(result_player)

    return jsonify(result)


@app.route("/maps", methods=["GET"])
def get_maps():
    return reference.get_Maps()


@app.route("/map", methods=["POST"])
def add_map():
    maps = reference.get_Maps()
    new_id = request.json.get("id")
    new_value = request.json.get("value")
    if new_id in maps:
        return jsonify({"error": "ID already exists"}), 400
    maps[new_id] = new_value

    sorted_maps = dict(sorted(maps.items(), key=lambda item: item[1]))
    reference.save_data("maps.json", sorted_maps)
    return jsonify({"message": "Civilization added"}), 201


@app.route("/games", methods=["POST"])
def game_route():

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
        player_id = 11628131
    else:
        api_result = static.call(url, params)

    maps = process_data(api_result, player_id)

    map_dicts = [item.to_dict() for item in maps]
    if settings.DEBUG:
        print(player_id)
        with open(f"./flux/flux-{player_id}.json", "w") as json_file:
            json.dump(api_result, json_file, indent=2)

        print(map_dicts)

        with open("./flux/result.json", "w") as json_file:
            json.dump(map_dicts, json_file, indent=2)

    all_players = get_all_players(maps)

    return jsonify({"players": all_players, "maps": map_dicts})


@app.route("/admin")
def home():
    return render_template("admin.html")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
