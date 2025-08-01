from reference import get_Maps, get_Players, CIVILIZATIONS
import requests

@staticmethod
def _to_dict_recursive(obj):
    if isinstance(obj, dict):
        return {k: _to_dict_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_dict_recursive(item) for item in obj]
    elif hasattr(obj, "__dict__"):  # Check if it's an object with attributes
        return _to_dict_recursive(obj.__dict__)
    else:
        return obj


@staticmethod
def format_timestamp(
    timestamp, timezone_str="GMT", display_abbr=False, round_to_nearest_15=False
):
    import pytz
    from datetime import datetime, timedelta

    if timestamp is None:
        return ""

    # Convert timestamp to datetime in specified timezone
    tz = pytz.timezone(timezone_str)
    dt = datetime.fromtimestamp(timestamp, tz)

    if round_to_nearest_15:
        minutes = dt.minute
        mod = minutes % 15

        if mod <= 10:
            # Truncate down
            new_minutes = minutes - mod
            dt = dt.replace(minute=new_minutes, second=0, microsecond=0)
        else:
            # Round up
            new_minutes = minutes + (15 - mod)
            dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(
                minutes=new_minutes
            )

    # Format date and time
    date_str = dt.strftime("%B %d, %Y - %H:%M")

    if display_abbr:
        # Get timezone abbreviation
        abbr = dt.strftime("%Z")
        return f"{date_str} {{{{Abbr/{abbr}}}}}"
    else:
        return date_str


@staticmethod
def get_civilization_lp(id):
    try:
        return CIVILIZATIONS.get(id, f"### Unknown - {id}")
    except KeyError:
        return f"Unknow_Key ### - {id}"


@staticmethod
def get_map_lp(id, label):
    try:
        return get_Maps().get(id, f"### Unknown - {id} - {label}")
    except KeyError:
        return f"Unknow_Key ### - {id} - {label}"


@staticmethod
def get_player_name_lp(id, label):
    try:
        return get_Players().get(id, f"{label} - ### Unknown - {id}")
    except KeyError:
        return f"Unknow_Key ### - {id} - {label} - "


@staticmethod
def decode_zlib_base64_tojson(encoded_data):
    import base64, zlib, json

    # Decode from base64
    compressed_data = base64.b64decode(encoded_data)

    # Decompress with zlib
    original_data = zlib.decompress(compressed_data)

    # If the original data is text, decode bytes to string
    json_text = original_data.decode("utf-8")

    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(json_text):
        try:
            json_decode, _ = decoder.raw_decode(json_text, pos)
            return json_decode
        except:
            break
    return None

@staticmethod
def call(url, params) -> str:
    # Make the GET request
    response = requests.get(url, params=params)

    # Check and print response
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)