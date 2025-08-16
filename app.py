from flask import Flask, request, jsonify, render_template
from services import RelicAPIClient, AOE4WorldAPIClient, StartGGGQLClient
from utils import static
from utils.utils import get_all_players
from utils.lp import get_participants
import reference

app = Flask(__name__)

## Admin Part


@app.route("/player", methods=["POST"])
def add_player():
    players = reference.get_Players()
    new_id = int(request.json.get("id"))
    new_value = request.json.get("value").strip()
    if new_id in players:
        return jsonify({"error": "ID already exists"}), 400
    players[new_id] = new_value

    sorted_maps = dict(sorted(players.items(), key=lambda item: item[1].lower()))
    static.save_data("players.json", sorted_maps)
    return jsonify({"message": "Player added"}), 201


@app.route("/search_player", methods=["POST"])
def search_player():
    text = request.json.get("text")
    result = AOE4WorldAPIClient.search_players(text)
    return jsonify(result)


@app.route("/map", methods=["POST"])
def add_map():
    new_id = request.json.get("id")
    new_value = request.json.get("value").strip()
    maps = reference.get_Maps()

    if new_id in maps:
        return jsonify({"error": "ID already exists"}), 400
    maps[new_id] = new_value

    sorted_maps = dict(sorted(maps.items(), key=lambda item: item[1]))
    static.save_data("maps.json", sorted_maps)
    return jsonify({"message": "Map added"}), 201


@app.route("/participants", methods=["GET"])
def get_participant():
    event_id = int(request.args.get("id"))
    with_flag = request.args.get("with_flag", "0") == "1"

    participants = StartGGGQLClient.get_standings(event_id)
    result = get_participants(participants, with_flag=with_flag)

    return result


## Draft Part


@app.route("/draft", methods=["POST"])
def add_draft():
    drafts = reference.get_Draft()
    new_key = request.json.get("id")
    print(new_key)
    new_value = request.json.get("value")
    drafts[new_key] = new_value

    static.save_data("draft.json", drafts)
    return jsonify({"message": "Draft added"}), 201


@app.route("/drafts", methods=["GET"])
def get_drafts():
    return reference.get_Draft()


## Home Part


@app.route("/players", methods=["GET"])
def get_players():
    unique_players = {}
    for key, value in reference.get_Players().items():
        if value not in unique_players.values():
            unique_players[key] = value
    return unique_players


@app.route("/games", methods=["POST"])
def game_route():

    data = request.get_json()
    player_id = int(data.get("player_id"))

    player_id2 = data.get("player_id2")
    if player_id2 is not None and player_id2 != "":
        players_ids = [int(player_id2)]
    else:
        players = reference.get_Players()

        player_reference = players.get(player_id)
        if player_reference:
            players_ids = [key for key, value in players.items() if value == player_reference]
        else:
            players_ids = [player_id]

    maps = RelicAPIClient.get_recent_match(players_ids=players_ids)

    map_dicts = [item.to_dict() for item in maps]
    all_players = get_all_players(maps, get_players())

    return jsonify({"players": all_players, "maps": map_dicts})


## Pages


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
