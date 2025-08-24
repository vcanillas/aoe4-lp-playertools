import json
from typing import List

import settings
from utils import static
from models.enums import RefType
from ..clients.relic_client import get_recent_match_history
from models.map import Map
from models.player import Player
from models.team import Team

REF_TYPE = RefType.RELIC 

class RelicAdapter:

    @staticmethod
    def get_recent_match(players_ids: List[int]) -> List[Map]:

        api_result = get_recent_match_history(players_ids=players_ids)

        if settings.USE_MOCK:
            players_ids = 11628131

        matches: List[Map] = []

        # Extract match history
        matchHistoryStats = api_result.get("matchHistoryStats")

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
            match = Map()
            match.matchtype_id = matchHistoryStat.get("id")
            match.start_game_time = matchHistoryStat.get("startgametime")
            match.date = static.format_date(
                matchHistoryStat.get("startgametime"), timezone_str="CET"
            )
            match.lp.date = static.format_date(
                matchHistoryStat.get("startgametime"),
                display_abbr=True,
                round_to_nearest_15=True,
            )
            match.completion_time = matchHistoryStat.get("completiontime")

            option = static.decode_zlib_base64_tojson(matchHistoryStat.get("options"))

            if option is not None:
                match.map_alias = option.get("localizedMapName")
                match.map_name_raw = option.get("mapName")
                match.lp.map = match.lp.get_map_lp(
                    REF_TYPE,
                    match.map_name_raw, match.map_alias, unknown=False
                )
                match.map_name = match.lp.get_map_lp(
                    REF_TYPE,
                    match.map_name_raw, match.map_alias
                )

                if settings.DEBUG:
                    match.option_raw = option

            # Loop through matchhistorymember to assign players to teams
            for member in matchHistoryStat.get("matchhistorymember", []):
                profile_id = member["profile_id"]

                profile = next(
                    (
                        profile
                        for profile in api_result["profiles"]
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

                player = Player()
                player.profile_id = profile_id

                if profile is not None:
                    player.name_raw = profile.get("alias", "")
                    player.set_lp_name()

                    player.civilization_id = member.get("civilization_id")
                    player.civilization_lp = player.get_civilization_lp(
                        REF_TYPE, member.get("civilization_id")
                    )

                team_id = result.get("resulttype")  # Team_id based on resulttype

                # Find team
                team = next(
                    (team for team in match.teams if team.team_id == team_id), None
                )
                if team is None:
                    team = Team()
                    team.team_id = team_id
                    team.result_type = result.get("resulttype")
                    match.teams.append(team)

                team.players.append(player)

            # Set Summary at the end
            if match.complete_data(players_ids):
                matches.append(match)

        if settings.DEBUG:
            with open(f"./flux/flux-{players_ids}.json", "w") as json_file:
                json.dump(api_result, json_file, indent=2)

            map_dicts = [item.to_dict() for item in matches]

            with open("./flux/result.json", "w") as json_file:
                json.dump(map_dicts, json_file, indent=2)

        return matches
