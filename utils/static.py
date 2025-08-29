from datetime import datetime


@staticmethod
def format_date(
    date, timezone_str="GMT", display_abbr=False, round_to_nearest_15=False
):
    import pytz
    from datetime import datetime, timedelta

    if date is None:
        return ""
    
    target_tz = pytz.timezone(timezone_str)

    # If timestamp is a string (ISO 8601), parse it
    if isinstance(date, str):
        # Parse ISO 8601 string, assuming UTC if ends with Z
        try:
            # Remove 'Z' if present and parse as UTC
            if date.endswith("Z"):
                dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
                dt = dt.replace(tzinfo=pytz.UTC)
            else:
                # For other ISO formats, you might want to handle differently
                dt = datetime.fromisoformat(date)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)

            dt = dt.astimezone(target_tz)
        except ValueError:
            # Fallback: parse without microseconds or handle error
            try:
                dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
                dt = dt.replace(tzinfo=pytz.UTC)
            except Exception:
                return ""
    else:
        # Convert timestamp (assumed to be Unix timestamp) to datetime in timezone
        dt = datetime.fromtimestamp(date, target_tz)

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
