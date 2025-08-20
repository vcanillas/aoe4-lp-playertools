import json, os, pickle
from datetime import datetime


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
def difference_timestamp(start_time: int, completion_time: int):
    dt1 = datetime.fromtimestamp(start_time)
    dt2 = datetime.fromtimestamp(completion_time)

    diff = abs(dt2 - dt1)

    # Extract hours and minutes
    total_minutes = diff.total_seconds() // 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)

    return f"{hours:02d}:{minutes:02d}"


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
def load_data_json(filename: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", filename)
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@staticmethod
def save_data_json(filename: str, data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", filename)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@staticmethod
def load_data_pickle(filename: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", filename)
    with open(data_path, "rb") as f:
        return pickle.load(f)

@staticmethod
def save_data_pickle(filename: str, data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", filename)
    with open(data_path, "wb") as f:
        pickle.dump(data, f)