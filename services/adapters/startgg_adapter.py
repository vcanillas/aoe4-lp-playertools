from ..clients.startgg_client import get_event_standings, get_event_id


class StartGGAdapter:

    @staticmethod
    def get_standings(event_name: int, with_flag=False):

        data_event_id = get_event_id(event_name)
        event_id = data_event_id["data"]["event"]["id"]

        data = get_event_standings(event_id=event_id)
        entries = data["data"]["event"]["standings"]["nodes"]

        result = ""
        for idx, node in enumerate(entries, start=1):
            name = node["entrant"]["participants"][0]["gamerTag"]
            line = f"|p{idx}={name} |p{idx}flag="
            if with_flag:
                flag = node["entrant"]["participants"][0]["user"]["location"]["country"]
                line += f"{flag}"
            result += line + "<br />"

        return result
