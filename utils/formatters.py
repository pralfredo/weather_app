from collections import defaultdict
from datetime import datetime, UTC


def format_current_payload(raw: dict, units: str) -> dict:
    weather = raw.get("weather", [{}])[0]
    main = raw.get("main", {})
    wind = raw.get("wind", {})
    sys = raw.get("sys", {})

    temp_unit = "°C" if units == "metric" else "°F"
    wind_unit = "m/s" if units == "metric" else "mph"

    return {
        "temp": round(main.get("temp", 0)),
        "feels_like": round(main.get("feels_like", 0)),
        "temp_unit": temp_unit,
        "condition": weather.get("description", "Unknown").title(),
        "icon": weather.get("icon", "01d"),
        "humidity": main.get("humidity", 0),
        "pressure": main.get("pressure", 0),
        "visibility": raw.get("visibility", 0),
        "wind_speed": round(wind.get("speed", 0), 1),
        "wind_unit": wind_unit,
        "sunrise": format_unix_time(sys.get("sunrise")),
        "sunset": format_unix_time(sys.get("sunset")),
    }


def format_hourly_payload(raw_items: list[dict], units: str, limit: int = 8) -> list[dict]:
    temp_unit = "°C" if units == "metric" else "°F"
    results = []

    for item in raw_items[:limit]:
        weather = item.get("weather", [{}])[0]
        results.append(
            {
                "time_label": format_unix_time(item.get("dt"), hour_only=True),
                "temp": round(item.get("main", {}).get("temp", 0)),
                "temp_unit": temp_unit,
                "icon": weather.get("icon", "01d"),
                "condition": weather.get("description", "Unknown").title(),
                "pop": round(float(item.get("pop", 0)) * 100),
            }
        )

    return results


def format_daily_payload(raw_items: list[dict], units: str, limit: int = 5) -> list[dict]:
    temp_unit = "°C" if units == "metric" else "°F"
    grouped: dict[str, list[dict]] = defaultdict(list)

    for item in raw_items:
        date_key = datetime.fromtimestamp(item["dt"], UTC).strftime("%Y-%m-%d")
        grouped[date_key].append(item)

    output = []

    for date_key, items in list(grouped.items())[:limit]:
        temps = [entry.get("main", {}).get("temp", 0) for entry in items]
        middle = items[len(items) // 2]
        weather = middle.get("weather", [{}])[0]
        pop_values = [round(float(entry.get("pop", 0)) * 100) for entry in items]

        output.append(
            {
                "date_label": datetime.strptime(date_key, "%Y-%m-%d").strftime("%a"),
                "temp_min": round(min(temps)),
                "temp_max": round(max(temps)),
                "temp_unit": temp_unit,
                "condition": weather.get("description", "Unknown").title(),
                "icon": weather.get("icon", "01d"),
                "pop": max(pop_values) if pop_values else 0,
            }
        )

    return output


def format_unix_time(timestamp: int | None, hour_only: bool = False) -> str:
    if not timestamp:
        return "—"

    dt = datetime.fromtimestamp(timestamp, UTC)
    return dt.strftime("%I %p").lstrip("0") if hour_only else dt.strftime("%I:%M %p").lstrip("0")