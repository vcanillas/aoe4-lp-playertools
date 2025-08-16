from typing import List
from utils import static, lp
import settings

class LPItem:
    def __init__(self):
        self.content = None
        self.date = None
        self.map = None


class Player:
    def __init__(self):
        self.profile_id = None
        self.name_raw = None
        self.name_lp = None
        self.name = None
        # self.name = None
        self.civilization_id = None
        self.civilization_lp = None

    def set_lp_name(self):
        self.name_lp = lp.get_player_name_lp(self.profile_id, self.name_raw, False)
        self.name = lp.get_player_name_lp(self.profile_id, self.name_raw, True)

    def set_civilization_id(self, value):
        self.civilization_id = value
        self.civilization_lp = lp.get_civilization_lp(value)

    def to_dict(self):
        return static._to_dict_recursive(self)


class Team:
    def __init__(self):
        self.team_id = None
        self.result_type = None
        self.players: List[Player] = []

    def to_dict(self):
        return static._to_dict_recursive(self)


class Map:
    def __init__(self):
        self.matchtype_id = None
        self.start_game_time = None
        self.date = None
        self.completion_time = None
        self.duration = None
        self.option_raw = None
        self.map_name_raw = None
        self.map_alias = None
        self.map_name = None
        self.summary = None
        self.lp: LPItem = LPItem()
        self.teams: List[Team] = []

    def set_start_game_time(self, value):
        self.start_game_time = value
        self.date = static.format_timestamp(value, timezone_str="CET")
        self.lp.date = static.format_timestamp(
            value, display_abbr=True, round_to_nearest_15=True
        )

    def set_option_raw(self, value):
        option = static.decode_zlib_base64_tojson(value)

        if option is not None:
            self.map_alias = option.get("localizedMapName")
            self.map_name_raw = option.get("mapName")
            self.lp.map = lp.get_map_lp(
                self.map_name_raw, self.map_alias, unknown=False
            )
            self.map_name = lp.get_map_lp(self.map_name_raw, self.map_alias)
            
            if settings.DEBUG:
                self.option_raw = option

    def to_dict(self):
        return static._to_dict_recursive(self)

    def complete_data(self, player1_id: List[int]):

        def reorder(player1_ids: List[int]):
            # Find the team and index where the player is located
            team_index = None
            for idx, team in enumerate(self.teams):
                for p in team.players:
                    if p.profile_id in player1_ids:
                        team_index = idx
                        break
                if team_index is not None:
                    break

            if team_index is None:
                print(f"Player with ID {player1_ids} not found.")
                return

            # Move the player to the top of their current team
            team = self.teams[team_index]
            # Remove the player from their original position
            player = next(p for p in team.players if p.profile_id in player1_ids)
            # Remove the player from the list
            team.players = [p for p in team.players if p.profile_id not in player1_ids]
            # Insert at the beginning
            team.players.insert(0, player)

            # Move the team to the front of the teams list
            self.teams.insert(0, self.teams.pop(team_index))

        def set_summary():
            # Check if there are teams
            if not self.teams:
                self.summary = f"{self.map_name} - No teams available"
                return

            # For simplicity, assume two teams
            team1 = self.teams[0]
            team2 = self.teams[1] if len(self.teams) > 1 else None

            # Helper to calculate total LP and get alias
            def team_info(team: Team):
                if not team.players:
                    return ("Unknown", "")
                alias = team.players[0].name_lp if team.players[0].name_lp else team.players[0].name_raw
                civ = team.players[0].civilization_lp
                winner = team.result_type == 1
                return (alias, civ, winner)

            alias1, lp1, winner1 = team_info(team1)
            alias2, lp2, winner2 = team_info(team2) if team2 else ("Unknown", 0)

            # Set the summary string
            self.summary = (
                f"{'' if len(self.teams[0].players) == 1 else 'Multi - '}"
                f"{self.date} "
                f"{alias1} {'👑 ' if winner1 else ''} ({lp1}) --- "
                f"{alias2} {'👑 ' if winner2 else ''} ({lp2}) - "
                f"{self.map_name}"
            )

        def set_lp():

            multi = False

            winning_team_index = None
            for i, team in enumerate(self.teams):
                if len(team.players) > 1:
                    multi = True
                if team.result_type == 1:
                    winning_team_index = i + 1
                    break

            players1 = ""
            civs1 = ""
            players2 = ""
            civs2 = ""

            for player in self.teams[0].players:
                civs1 += player.civilization_lp + ","
                players1 += player.name_lp + ","

            for player in self.teams[1].players:
                civs2 += player.civilization_lp + ","
                players2 += player.name_lp + ","

            # Important: Remove trailing ", "
            civs1 = civs1.rstrip(",")
            civs2 = civs2.rstrip(",")
            players1 = players1.rstrip(",")
            players2 = players2.rstrip(",")

            output = (
                "{{Map\n"
                + (f"        |map={self.lp.map}|winner={winning_team_index}\n")
                + (f"        |players1={players1}\n" if multi else "")
                + (f"        |civs1={civs1}\n")
                + (f"        |players2={players2}\n" if multi else "")
                + (f"        |civs2={civs2}\n")
                + ("    }}")
            )

            self.lp.content = output

        def set_duration():
            self.duration = static.difference_timestamp(self.start_game_time, self.completion_time)

        if len(self.teams) > 1:
            reorder(player1_id)
            set_summary()
            set_lp()
            set_duration()
            return True
        else:
            return False
