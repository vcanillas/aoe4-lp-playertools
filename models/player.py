from models.base_model import BaseModel
from models.enums import RefType
from models.reference import CIVILIZATIONS, get_Players


class Player(BaseModel):
    def __init__(self):
        self.profile_id = None
        self.name_raw = None
        self.name_lp = None
        self.name = None
        self.civilization_id = None
        self.civilization_lp = None

    def set_lp_name(self):
        self.name_lp = self.get_player_name_lp(self.profile_id, self.name_raw, False)
        self.name = self.get_player_name_lp(self.profile_id, self.name_raw, True)

    def get_player_name_lp(self, id, label, unknown=True) -> str:
        try:
            return get_Players().get(
                id, f"{label} - ### Unknown - {id}" if unknown else label
            )
        except KeyError:
            return f"Unknown_Key ### - {id} - {label} - "

    @staticmethod
    def get_civilization_lp(ref: RefType, value: str) -> str:
        ref_str = ref.value
        for civ_code, civ_info in CIVILIZATIONS.items():
            if civ_info.get(ref_str) == value:
                return civ_code
        return f"### Unknown - {value}"
