from typing import List

from models.base_model import BaseModel
from models.player import Player


class Team(BaseModel):
    def __init__(self):
        self.team_id = None
        self.result_type = None
        self.players: List[Player] = []
