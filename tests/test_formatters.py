from utils.formatters import (
    format_current_payload,
    format_daily_payload,
    format_hourly_payload,
    format_unix_time,
)


def test_format_unix_time_returns_dash_for_none():
    assert format_unix_time(None) == "—"


def test_format_unix_time_hour_only():
    result = format_unix_time(1700000000, hour_only=True)
    assert result.endswith("AM") or result.endswith("PM")


def test_format_current_payload_metric():
    raw = {
        "weather": [{"description": "broken clouds", "icon": "04d"}],
        "main": {
            "temp": 12.4,
            "feels_like": 10.8,
            "humidity": 55,
            "pressure": 1012,
        },
        "wind": {"speed": 4.2},
        "sys": {"sunrise": 1700000000, "sunset": 1700030000},
        "visibility": 10000,
    }

    result = format_current_payload(raw, "metric")
    assert result["temp"] == 12
    assert result["feels_like"] == 11
    assert result["temp_unit"] == "°C"
    assert result["condition"] == "Broken Clouds"
    assert result["icon"] == "04d"
    assert result["humidity"] == 55
    assert result["pressure"] == 1012
    assert result["wind_speed"] == 4.2
    assert result["wind_unit"] == "m/s"
    assert result["visibility"] == 10000
    assert result["sunrise"] != "—"
    assert result["sunset"] != "—"


def test_format_current_payload_imperial():
    raw = {
        "weather": [{"description": "clear sky", "icon": "01d"}],
        "main": {"temp": 70.1, "feels_like": 69.8, "humidity": 40, "pressure": 1008},
        "wind": {"speed": 8.6},
        "sys": {"sunrise": 1700000000, "sunset": 1700030000},
        "visibility": 9000,
    }

    result = format_current_payload(raw, "imperial")
    assert result["temp_unit"] == "°F"
    assert result["wind_unit"] == "mph"


def test_format_hourly_payload_limit():
    raw_items = [
        {
            "dt": 1700000000 + i * 3600,
            "main": {"temp": 10 + i},
            "weather": [{"description": "cloudy", "icon": "03d"}],
            "pop": 0.12,
        }
        for i in range(10)
    ]

    result = format_hourly_payload(raw_items, "metric", limit=3)
    assert len(result) == 3
    assert result[0]["temp_unit"] == "°C"
    assert result[0]["condition"] == "Cloudy"
    assert result[0]["pop"] == 12


def test_format_daily_payload_groups_by_day():
    raw_items = [
        {
            "dt": 1700000000,
            "main": {"temp": 10},
            "weather": [{"description": "clear sky", "icon": "01d"}],
            "pop": 0.1,
        },
        {
            "dt": 1700010800,
            "main": {"temp": 14},
            "weather": [{"description": "clear sky", "icon": "01d"}],
            "pop": 0.2,
        },
        {
            "dt": 1700086400,
            "main": {"temp": 8},
            "weather": [{"description": "rain", "icon": "10d"}],
            "pop": 0.7,
        },
    ]

    result = format_daily_payload(raw_items, "metric", limit=5)
    assert len(result) >= 2
    assert "date_label" in result[0]
    assert "temp_min" in result[0]
    assert "temp_max" in result[0]
    assert result[0]["temp_unit"] == "°C"