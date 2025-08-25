from flask import Blueprint, request, jsonify
from typing import List
from collections import defaultdict
import re


tournament_bp = Blueprint("tournament", __name__)

## Tournament Part


@draft_bp.route("/tournament", methods=["POST"])
def update_tournament():
    players_input = request.json.get("players")
    players = parse_input(players_input)
    players_id = get_players_from_name(players)

    maps = RelicAdapter.get_recent_match(players_ids=players_ids)
    map_dicts = [item.to_dict() for item in maps]
    all_players = get_all_players(maps, get_players_unique())

    live_game = bool(data.get("live_game"))
    if live_game:
        maps_live = AOE4WorldAdapter.get_live_games(players_ids=players_ids)
        if maps_live is not None:
            map_live_dicts = [item.to_dict() for item in maps_live]
            map_dicts = map_live_dicts + map_dicts

    return jsonify("maps": map_dicts})


def parse_input(input_str: str) -> List[str]:
    players = []

    if '=' in input_str:
        # Find all key-value pairs
        pairs = re.findall(r'\|([^|=]+)=([^|]*)', input_str)
        for key, value in pairs:
            key = key.strip()
            value = value.strip()
            # Check if key relates to a player
            if re.match(r'p\d*', key, re.IGNORECASE):  # keys like p1, p2, p3, p4
                if value:
                    players.append(value)
    else:
        # Assume comma-separated list
        players = [item.strip() for item in input_str.split(',') if item.strip()]

    return players

def get_players_from_name(players_name: List[str]) -> List[int]:
    players_reference = reference.get_Players()

    name_to_ids = defaultdict(list)
    for id, name in players_reference.items():
        name_to_ids[name].append(id)

    # Get list of IDs for these names
    result_ids = []
    for name in players_name:
        result_ids.extend(name_to_ids.get(name, []))

    return result_ids