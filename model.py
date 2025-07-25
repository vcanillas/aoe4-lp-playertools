from typing import List
import static


class Player:
    def __init__(self):
        self.profile_id = None
        self.alias = None
        self.name_lp = None
        # self.name = None
        self.civilization_id = None
        self.civilization_lp = None

    def set_lp_name(self):
        self.name_lp = static.get_player_name_lp(self.profile_id, self.alias)

    def set_civilization_id(self, value):
        self.civilization_id = value
        self.civilization_lp = static.get_civilization_lp(value)

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
        self.date_lp = None
        self.date = None
        self.completion_time = None
        self.option_raw = None
        self.map_name_raw = None
        self.map_name = None
        self.map_lp = None
        self.summary = None
        self.lp = None
        self.teams: List[Team] = []

    def set_start_game_time(self, value):
        self.start_game_time = value
        self.date = static.format_timestamp(value, timezone_str="CET")
        self.date_lp = static.format_timestamp(
            value, display_abbr=True, round_to_nearest_15=True
        )

    def set_option_raw(self, value):
        # self.option_raw = value
        option = static.decode_zlib_base64_tojson(value)
        if option is not None:
            self.map_name = option.get("localizedMapName")
            self.map_name_raw = option.get("mapName")
            self.map_lp = static.get_map_lp(self.map_name_raw, self.map_name)

    def to_dict(self):
        return static._to_dict_recursive(self)

    def complete_data(self, player1_id: int):

        def reorder(player1_id: int):
            # Find the team and index where the player is located
            team_index = None
            for idx, team in enumerate(self.teams):
                for p in team.players:
                    if p.profile_id == player1_id:
                        team_index = idx
                        break
                if team_index is not None:
                    break

            if team_index is None:
                print(f"Player with ID {player1_id} not found.")
                return

            # Move the player to the top of their current team
            team = self.teams[team_index]
            # Remove the player from their original position
            player = next(p for p in team.players if p.profile_id == player1_id)
            # Remove the player from the list
            team.players = [p for p in team.players if p.profile_id != player1_id]
            # Insert at the beginning
            team.players.insert(0, player)

            # Move the team to the front of the teams list
            self.teams.insert(0, self.teams.pop(team_index))

        def set_summary():
            # Check if there are teams
            if not self.teams:
                self.summary = f"{self.map_lp} - No teams available"
                return

            # For simplicity, assume two teams
            team1 = self.teams[0]
            team2 = self.teams[1] if len(self.teams) > 1 else None

            # Helper to calculate total LP and get alias
            def team_info(team: Team):
                if not team.players:
                    return ("Unknown", "")
                alias = team.players[0].name_lp
                civ = team.players[0].civilization_lp
                winner = team.result_type == 1
                return (alias, civ, winner)

            alias1, lp1, winner1 = team_info(team1)
            alias2, lp2, winner2 = team_info(team2) if team2 else ("Unknown", 0)

            # Set the summary string
            self.summary = (
                f"{'' if len(self.teams[0].players) == 1 else 'Multi - '}"
                f"{self.date} "
                f"{alias1} {'👑 ' if winner1 else ''} ({lp1}) ||| "
                f"{alias2} {'👑 ' if winner2 else ''}({lp2}) - "
                f"{self.map_lp}"
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
                + (f"        |map={self.map_lp}|winner={winning_team_index}\n")
                + (f"        |players1={players1}\n" if multi else "")
                + (f"        |civs1={civs1}\n")
                + (f"        |players2={players2}\n" if multi else "")
                + (f"        |civs2={civs2}\n")
                + ("    }}")
            )

            self.lp = output

        if len(self.teams) > 1:
            reorder(player1_id)
            set_summary()
            set_lp()
            return True
        else:
            return False
