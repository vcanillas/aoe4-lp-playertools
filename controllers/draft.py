from flask import Blueprint, request, jsonify

from models import reference
from repositories.json_repository import JsonRepository
from services.adapters.aoe4world_adapter import AOE4WorldAdapter

draft_bp = Blueprint("draft", __name__)

## Draft Part


@draft_bp.route("/draft", methods=["POST"])
def add_draft():
    drafts = reference.get_Draft()
    new_key = request.json.get("id")
    new_value = request.json.get("value")
    drafts[new_key] = new_value

    JsonRepository.save_data("draft.json", drafts)
    return jsonify({"message": "Draft added"}), 201


@draft_bp.route("/drafts", methods=["GET"])
def get_drafts():
    return reference.get_Draft()


@draft_bp.route("/draft", methods=["GET"])
def search_drafts():
    preset = request.args.get("preset")
    result = AOE4WorldAdapter.get_drafts(preset)
    return jsonify(result)
