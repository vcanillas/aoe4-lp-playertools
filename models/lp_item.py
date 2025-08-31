from models.enums import RefType
from models.reference import get_Maps
from utils.static import extract_map_name


class LPItem:
    def __init__(self):
        self.content = None
        self.date = None
        self.map = None

    @staticmethod
    def get_map_lp(refType: RefType, id, label, unknown=True) -> str:
        try:
            if refType == RefType.AOE4WORLD:
                extracted = extract_map_name(id)

                return next(
                    (v for v in get_Maps().values() if v == extracted), None
                ) or (f"{label} - ### Unknown - {id}" if unknown else label)

            elif refType == RefType.RELIC:
                return get_Maps().get(
                    id, f"{label} - ### Unknown - {id}" if unknown else label
                )
            else:
                return f"Unknown_Key ### - {id} - {label}"
        except KeyError:
            return f"Unknown_Key ### - {id} - {label}"
