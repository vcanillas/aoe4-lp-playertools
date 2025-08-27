from flask import Blueprint, request, jsonify

from repositories.json_repository import JsonRepository
from repositories.pickle_repository import PickleRepository
from services.adapters.startgg_adapter import StartGGAdapter
from services.adapters.relic_adapter import RelicAdapter
from services.adapters.aoe4world_adapter import AOE4WorldAdapter
import models.reference as reference

admin_bp = Blueprint("admin", __name__)

## Admin Part


@admin_bp.route("/player", methods=["POST"])
def add_player():
    players = reference.get_Players()
    new_id = int(request.json.get("id"))
    new_value = request.json.get("value").strip()
    if new_id in players:
        return jsonify({"error": "ID already exists"}), 409
    players[new_id] = new_value

    sorted_maps = dict(sorted(players.items(), key=lambda item: item[1].lower()))
    PickleRepository.save_data("players.pkl", sorted_maps)
    return jsonify({"message": "Player added"}), 201


@admin_bp.route("/search_player", methods=["POST"])
def search_player():
    text = request.json.get("text")
    result = AOE4WorldAdapter.search_players(text)
    return jsonify(result)


@admin_bp.route("/map", methods=["POST"])
def add_map():
    new_id = request.json.get("id")
    new_value = request.json.get("value").strip()
    maps = reference.get_Maps()

    if new_id in maps:
        return jsonify({"error": "ID already exists"}), 409
    maps[new_id] = new_value

    sorted_maps = dict(sorted(maps.items(), key=lambda item: item[1]))
    JsonRepository.save_data("maps.json", sorted_maps)
    return jsonify({"message": "Map added"}), 201


@admin_bp.route("/participants", methods=["GET"])
def get_participant():
    event_name = request.args.get("id")
    with_flag = request.args.get("with_flag", "0") == "1"

    return StartGGAdapter.get_standings(event_name=event_name, with_flag=with_flag)
