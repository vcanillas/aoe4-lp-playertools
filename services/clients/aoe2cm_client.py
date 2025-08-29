import json
import requests

AOE2CM_URL_API = "https://aoe2cm.net/api"


@staticmethod
def get_draft_detail(id: str):
    url = AOE2CM_URL_API + "/draft/" + id

    # Make the GET request
    response = requests.get(url)

    # Check and print response
    if response.status_code == 200:
        return response.json()
    else:
        raise ("Error:", response.status_code, response.text)
