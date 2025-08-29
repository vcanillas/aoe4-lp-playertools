from flask import Blueprint, request, jsonify

from services.adapters.relic_adapter import RelicAdapter
from services.adapters.aoe4world_adapter import AOE4WorldAdapter
from utils.utils import get_all_players
import models.reference as reference


home_bp = Blueprint("home", __name__)


## Home Part


@home_bp.route("/players", methods=["GET"])
def get_players_unique():
    unique_players = {}
    for key, value in reference.get_Players().items():
        if value not in unique_players.values():
            unique_players[key] = value
    return unique_players


@home_bp.route("/games", methods=["POST"])
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
            players_ids = [
                key for key, value in players.items() if value == player_reference
            ]
        else:
            players_ids = [player_id]

    maps = RelicAdapter.get_recent_match(players_ids=players_ids)
    map_dicts = [item.to_dict() for item in maps]
    all_players = get_all_players(maps, get_players_unique())

    live_game = bool(data.get("live_game"))
    if live_game:
        maps_live = AOE4WorldAdapter.get_live_games(players_ids=players_ids)
        if maps_live is not None:
            map_live_dicts = [item.to_dict() for item in maps_live]
            map_dicts = map_live_dicts + map_dicts

    return jsonify({"players": all_players, "maps": map_dicts})
