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
    new_value = request.json.get("value")
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
    new_value = request.json.get("value")
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


## Home Part


@app.route("/players", methods=["GET"])
def get_players():
    return reference.get_Players()


@app.route("/games", methods=["POST"])
def game_route():

    data = request.get_json()
    player_id = int(data.get("player_id"))

    player2 = data.get("player_id2")
    if player2 is not None and player2 != "":
        player_id = int(player2)

    maps = RelicAPIClient.get_recent_match(player_id=player_id)

    map_dicts = [item.to_dict() for item in maps]
    all_players = get_all_players(maps, reference.get_Players())

    return jsonify({"players": all_players, "maps": map_dicts})


## Pages


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
