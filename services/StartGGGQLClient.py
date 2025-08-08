import requests
import settings

START_GG_API_URL = "https://api.start.gg/gql/alpha"


def get_standings(event_id: int):

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
        data = response.json()
        return data
    else:
        raise (
            f"Query failed to run by returning code of {response.status_code}. {response.text}"
        )
