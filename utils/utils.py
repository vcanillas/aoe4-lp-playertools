from typing import List
import model


@staticmethod
def get_all_players(matches: List[model.Map], players: dict[int, str]):
    # Make a shallow copy of PLAYERS to avoid modifying the original list
    updated_players = players.copy()

    for match in matches:
        for team in match.teams:
            for player in team.players:
                # If player not already in players
                if player.profile_id not in updated_players:
                    # Create new player object
                    updated_players[player.profile_id] = player.alias

    return updated_players
