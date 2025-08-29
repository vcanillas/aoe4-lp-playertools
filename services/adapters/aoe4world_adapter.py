from typing import Any, List
from models.enums import RefType
from models.map import Map
from models.player import Player
import models.reference as reference
from models.team import Team
from services.clients import aoe4world_client
from utils import static

REF_TYPE = RefType.AOE4WORLD


class AOE4WorldAdapter:

    @staticmethod
    def search_players(text: str):
        result = []
        lp_players = reference.get_Players()

        api_result = aoe4world_client.search_players(text=text)

        for player in api_result["players"]:
            result_player = {
                "name": player.get("name"),
                "profile_id": player.get("profile_id"),
                "country": player.get("country"),
                "steam_id": player.get("steam_id"),
                "lp_name": lp_players.get(player.get("profile_id"), ""),
            }
            result.append(result_player)

        return result

    @staticmethod
    def get_player(id: str):
        result = []
        lp_players = reference.get_Players()

        api_result = aoe4world_client.get_player(id=id)
        result_player = {
            "name": api_result.get("name"),
            "profile_id": api_result.get("profile_id"),
            "country": api_result.get("country"),
            "steam_id": api_result.get("steam_id"),
            "lp_name": lp_players.get(api_result.get("profile_id"), ""),
        }
        result.append(result_player)

        return result

    @staticmethod
    def get_drafts(text: str) -> dict[str, Any]:
        api_result = aoe4world_client.get_drafts(text=text)

        result = []
        for draft in api_result["drafts"]:
            drafts = {
                "draft_id": draft.get("draft"),
                "draft_link": "http://aoe2cm.net/draft/" + draft.get("draft"),
                "draft_name": draft.get("preset_name"),
                "player_1": draft.get("host_name"),
                "player_2": draft.get("guest_name"),
                "date": draft.get("created_at"),
            }
            result.append(drafts)

        return result

    def get_live_games(players_ids: List[int]) -> List[Map]:
        api_result = aoe4world_client.get_live_games(players_ids=players_ids)

        matches: List[Map] = []

        if api_result.get("count") == 0:
            return None
        else:
            # Extract match history
            games = api_result.get("games")

            # Sort matches by 'matchstartdate' descending
            games = sorted(games, key=lambda x: x["started_at"], reverse=True)

            for game in games:
                match = Map()
                match.matchtype_id = game.get("game_id")
                match.start_game_time = game.get("started_at")
                match.date = static.format_date(
                    game.get("started_at"), timezone_str="CET"
                )
                match.lp.date = static.format_date(
                    game.get("started_at"),
                    display_abbr=True,
                    round_to_nearest_15=True,
                )
                match.completion_time = None

                match.map_alias = game.get("map")
                match.map_name_raw = game.get("map")
                match.lp.map = match.lp.get_map_lp(
                    REF_TYPE, match.map_name_raw, match.map_alias, unknown=False
                )
                match.map_name = match.lp.get_map_lp(
                    REF_TYPE, match.map_name_raw, match.map_alias
                )

                for index, teams in enumerate(game.get("teams", [])):
                    team_id = index

                    team = Team()
                    team.team_id = team_id
                    team.result_type = None
                    match.teams.append(team)

                    for team_player in teams:
                        player_player = team_player.get("player")
                        player = Player()
                        player.profile_id = player_player.get("profile_id")
                        player.name_raw = player_player.get("name", "")
                        player.set_lp_name()

                        player.civilization_id = player_player.get("civilization")
                        player.civilization_lp = player.get_civilization_lp(
                            REF_TYPE, player_player.get("civilization")
                        )

                        # Find team
                        teams = next(
                            (team for team in match.teams if team.team_id == team_id),
                            None,
                        )

                        teams.players.append(player)

                # Set Summary at the end
                if match.complete_data(players_ids):
                    matches.append(match)

            return matches
