from app import app


def test_home_route_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Weather Window" in response.data


def test_test_route_works(client):
    response = client.get("/test")
    assert response.status_code == 200
    assert response.data == b"test route works"


def test_api_weather_requires_city(client):
    response = client.get("/api/weather")
    assert response.status_code == 400
    assert response.get_json() == {"error": "City is required."}


def test_api_weather_rejects_invalid_country(client):
    response = client.get("/api/weather?city=Boston&country=USA")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Country must be a 2-letter code."}


def test_api_weather_returns_404_when_location_missing(client, monkeypatch):
    monkeypatch.setattr("app.geocode_location", lambda city, country: None)

    response = client.get("/api/weather?city=Boston&country=US")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Location not found."}


def test_api_weather_returns_502_when_current_weather_missing(client, monkeypatch):
    monkeypatch.setattr(
        "app.geocode_location",
        lambda city, country: {"name": "Boston", "country": "US", "lat": 42.36, "lon": -71.06},
    )
    monkeypatch.setattr("app.fetch_current_weather", lambda lat, lon, units: None)
    monkeypatch.setattr("app.fetch_forecast", lambda lat, lon, units: [{"dt": 1}])

    response = client.get("/api/weather?city=Boston&country=US")
    assert response.status_code == 502
    assert response.get_json() == {"error": "Weather data unavailable."}


def test_api_weather_returns_502_when_forecast_missing(client, monkeypatch):
    monkeypatch.setattr(
        "app.geocode_location",
        lambda city, country: {"name": "Boston", "country": "US", "lat": 42.36, "lon": -71.06},
    )
    monkeypatch.setattr("app.fetch_current_weather", lambda lat, lon, units: {"ok": True})
    monkeypatch.setattr("app.fetch_forecast", lambda lat, lon, units: None)

    response = client.get("/api/weather?city=Boston&country=US")
    assert response.status_code == 502
    assert response.get_json() == {"error": "Weather data unavailable."}


def test_api_weather_success_response_shape(client, monkeypatch):
    monkeypatch.setattr(
        "app.geocode_location",
        lambda city, country: {"name": "Boston", "country": "US", "lat": 42.36, "lon": -71.06},
    )
    monkeypatch.setattr("app.fetch_current_weather", lambda lat, lon, units: {"raw": "current"})
    monkeypatch.setattr("app.fetch_forecast", lambda lat, lon, units: [{"raw": "forecast"}])
    monkeypatch.setattr(
        "app.format_current_payload",
        lambda current, units: {
            "temp": 12,
            "temp_unit": "°C",
            "condition": "Cloudy",
            "humidity": 55,
            "wind_speed": 4.2,
        },
    )
    monkeypatch.setattr(
        "app.format_hourly_payload",
        lambda forecast, units, limit=8: [
            {"time_label": "3 PM", "temp": 13, "temp_unit": "°C", "pop": 10}
        ],
    )
    monkeypatch.setattr(
        "app.format_daily_payload",
        lambda forecast, units, limit=5: [
            {"date_label": "Tue", "temp_min": 10, "temp_max": 14, "temp_unit": "°C"}
        ],
    )
    monkeypatch.setattr(
        "app.build_planner_insights",
        lambda current, hourly: {
            "outfit": "Jacket",
            "best_time": "3 PM",
            "rain_soon": False,
            "comfort_score": 78,
        },
    )
    monkeypatch.setattr(
        "app.summarize_current_weather",
        lambda current, insights: "Cool and cloudy right now.",
    )

    response = client.get("/api/weather?city=Boston&country=US&units=metric")
    assert response.status_code == 200

    data = response.get_json()
    assert data["location"]["city"] == "Boston"
    assert data["location"]["country"] == "US"
    assert data["location"]["lat"] == 42.36
    assert data["location"]["lon"] == -71.06
    assert data["current"]["temp"] == 12
    assert data["hourly"][0]["time_label"] == "3 PM"
    assert data["daily"][0]["date_label"] == "Tue"
    assert data["insights"]["best_time"] == "3 PM"
    assert data["summary"] == "Cool and cloudy right now."


def test_api_weather_allows_blank_country(client, monkeypatch):
    monkeypatch.setattr(
        "app.geocode_location",
        lambda city, country: {"name": city, "country": "", "lat": 1.0, "lon": 2.0},
    )
    monkeypatch.setattr("app.fetch_current_weather", lambda lat, lon, units: {"raw": "current"})
    monkeypatch.setattr("app.fetch_forecast", lambda lat, lon, units: [{"raw": "forecast"}])
    monkeypatch.setattr("app.format_current_payload", lambda current, units: {"temp": 20})
    monkeypatch.setattr("app.format_hourly_payload", lambda forecast, units, limit=8: [])
    monkeypatch.setattr("app.format_daily_payload", lambda forecast, units, limit=5: [])
    monkeypatch.setattr(
        "app.build_planner_insights",
        lambda current, hourly: {
            "outfit": "T-shirt",
            "best_time": "4 PM",
            "rain_soon": False,
            "comfort_score": 90,
        },
    )
    monkeypatch.setattr(
        "app.summarize_current_weather",
        lambda current, insights: "Warm and comfortable.",
    )

    response = client.get("/api/weather?city=Kathmandu")
    assert response.status_code == 200
    data = response.get_json()
    assert data["location"]["city"] == "Kathmandu"