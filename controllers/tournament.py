from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from typing import List, Tuple
from collections import defaultdict
import re

from models import reference
from models.map import Map
from services.adapters.aoe4world_adapter import AOE4WorldAdapter
from services.adapters.relic_adapter import RelicAdapter


tournament_bp = Blueprint("tournament", __name__)

## Tournament Part


@tournament_bp.route("/tournament", methods=["POST"])
def update_tournament():
    players_input = request.json.get("players")
    players = parse_input(players_input)
    players_ids, missing_players = get_players_from_name(players)

    maps = RelicAdapter.get_recent_match(players_ids=players_ids)
    # maps_dicts = [item.to_dict() for item in maps]

    maps_live = AOE4WorldAdapter.get_live_games(players_ids=players_ids)
    if maps_live is not None:
        maps = maps + maps_live

    maps_filtered = filtered_map(maps)
    map_dicts = [item.to_dict() for item in maps_filtered]

    return jsonify({"maps": map_dicts, "missing": missing_players})


def parse_input(input_str: str) -> List[str]:
    players = []

    if "=" in input_str:
        # Find all key-value pairs
        pairs = re.findall(r"\|([^|=]+)=([^|]*)", input_str)
        for key, value in pairs:
            key = key.strip()
            value = value.strip()
            # Check if key relates to a player
            if re.match(r"p\d*", key, re.IGNORECASE):  # keys like p1, p2, p3, p4
                if value:
                    players.append(value)
    else:
        # Assume comma-separated list
        players = [item.strip() for item in input_str.split(",") if item.strip()]

    return players


def get_players_from_name(players_name: List[str]) -> Tuple[List[int], List[str]]:
    players_reference = reference.get_Players()

    name_to_ids = defaultdict(list)
    for id, name in players_reference.items():
        name_to_ids[name].append(id)

    # Get list of IDs for these names
    result_ids = []
    for name in players_name:
        result_ids.extend(name_to_ids.get(name, []))

    missing_players = [name for name in players_name if name not in name_to_ids]

    return result_ids, missing_players


def filtered_map(map_dicts: List[Map]) -> List[Map]:
    now = datetime.now(timezone.utc)

    filtered_maps: List[Map] = []

    for map in map_dicts:
        date_value = map.date
        try:
            m_date = datetime.strptime(date_value, "%B %d, %Y - %H:%M").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue

        if m_date >= now - timedelta(hours=3):
            filtered_maps.append(map)

    latest_maps = {}
    for map in filtered_maps:
        match_id = map.matchtype_id
        if match_id not in latest_maps:
            latest_maps[match_id] = map

    # Sort the filtered maps by date, newest first (descending)
    sorted_maps = sorted(
        latest_maps.values(),
        key=lambda m: datetime.strptime(m.date, "%B %d, %Y - %H:%M").replace(
            tzinfo=timezone.utc
        ),
        reverse=True,
    )

    return sorted_maps
