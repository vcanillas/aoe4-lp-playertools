import requests

import settings

START_GG_API_URL = "https://api.start.gg/gql/alpha"


def get_event_id(slug: str) -> int:
    query = """
query getEventId($slug: String) {
  event(slug: $slug) {
    id
  }
}
    """
    variables = {"slug": slug}

    headers = {
        "Authorization": "Bearer " + settings.START_GG_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {"query": query, "variables": variables}

    response = requests.post(START_GG_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise (
            f"Query failed to run by returning code of {response.status_code}. {response.text}"
        )


def get_event_standings(event_id: int):

    query = """
query EventStandings($eventId: ID!, $page: Int!, $perPage: Int!) {
  event(id: $eventId) {
    id
    name
    standings(query: {
      perPage: $perPage,
      page: $page
    }){
      nodes {
        entrant {
          participants {
          	gamerTag,
          	 user {
              location {
                country
              }
            }
          }
        }
      }
    }
  }
}
    """

    variables = {"eventId": event_id, "page": 1, "perPage": 100}

    headers = {
        "Authorization": "Bearer " + settings.START_GG_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {"query": query, "variables": variables}

    response = requests.post(START_GG_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise (
            f"Query failed to run by returning code of {response.status_code}. {response.text}"
        )
