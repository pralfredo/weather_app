import os
from typing import Any

import requests

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_api_key() -> str:
    return os.getenv("OPENWEATHER_API_KEY", "").strip()


def geocode_location(city: str, country: str = "") -> dict[str, Any] | None:
    api_key = get_api_key()
    if not api_key:
        print("GEOCODE: missing API key")
        return None

    query = city if not country else f"{city},{country}"

    try:
        response = requests.get(
            GEOCODE_URL,
            params={
                "q": query,
                "limit": 5,
                "appid": api_key,
            },
            timeout=10,
        )
        print("GEOCODE API KEY PRESENT:", bool(api_key))
        print("GEOCODE QUERY:", query)
        print("GEOCODE STATUS:", response.status_code)
        print("GEOCODE BODY:", response.text[:500])

        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        print("GEOCODE ERROR:", exc)
        return None

    if not isinstance(data, list) or not data:
        print("GEOCODE: no matches returned")
        return None

    item = data[0]
    if "lat" not in item or "lon" not in item:
        print("GEOCODE: missing lat/lon in first result")
        return None

    return item


def fetch_current_weather(lat: float, lon: float, units: str) -> dict[str, Any] | None:
    api_key = get_api_key()
    if not api_key:
        print("CURRENT: missing API key")
        return None

    try:
        response = requests.get(
            CURRENT_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": units,
            },
            timeout=10,
        )
        print("CURRENT STATUS:", response.status_code)
        print("CURRENT BODY:", response.text[:300])

        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        print("CURRENT ERROR:", exc)
        return None

    if not isinstance(data, dict):
        print("CURRENT: invalid JSON shape")
        return None

    return data


def fetch_forecast(lat: float, lon: float, units: str) -> list[dict[str, Any]] | None:
    api_key = get_api_key()
    if not api_key:
        print("FORECAST: missing API key")
        return None

    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": units,
            },
            timeout=10,
        )
        print("FORECAST STATUS:", response.status_code)
        print("FORECAST BODY:", response.text[:300])

        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        print("FORECAST ERROR:", exc)
        return None

    if not isinstance(data, dict):
        print("FORECAST: invalid JSON shape")
        return None

    forecast_items = data.get("list")
    if not isinstance(forecast_items, list):
        print("FORECAST: missing list")
        return None

    return forecast_items