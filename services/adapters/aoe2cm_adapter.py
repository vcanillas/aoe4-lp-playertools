from typing import List
from services.clients import aoe2cm_client


class AOE2CaptainModeAdapter:

    @staticmethod
    def get_draft_detail(id: str) -> List[str]:
        api_result = aoe2cm_client.get_draft_detail(id=id)

        result = []
        for event in api_result["events"]:
            if event.get("actionType") == "pick":
                result.append(event.get("chosenOptionId"))

        return result
