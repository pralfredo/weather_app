from types import SimpleNamespace

from services import weather_api


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text="", raise_error=None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self._raise_error = raise_error

    def raise_for_status(self):
        if self._raise_error:
            raise self._raise_error

    def json(self):
        return self._json_data


def test_get_api_key_reads_env(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "abc123")
    assert weather_api.get_api_key() == "abc123"


def test_geocode_location_returns_none_without_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    assert weather_api.geocode_location("Boston", "US") is None


def test_geocode_location_success(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")

    def fake_get(url, params, timeout):
        assert params["q"] == "Boston,US"
        assert params["appid"] == "key"
        return DummyResponse(
            json_data=[{"name": "Boston", "country": "US", "lat": 42.36, "lon": -71.06}],
            text='[{"name":"Boston"}]',
        )

    monkeypatch.setattr(weather_api.requests, "get", fake_get)
    result = weather_api.geocode_location("Boston", "US")
    assert result["name"] == "Boston"
    assert result["lat"] == 42.36


def test_geocode_location_returns_none_for_empty_list(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")
    monkeypatch.setattr(
        weather_api.requests,
        "get",
        lambda url, params, timeout: DummyResponse(json_data=[], text="[]"),
    )
    assert weather_api.geocode_location("Boston", "US") is None


def test_geocode_location_returns_none_on_request_error(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")

    def fake_get(url, params, timeout):
        raise weather_api.requests.RequestException("boom")

    monkeypatch.setattr(weather_api.requests, "get", fake_get)
    assert weather_api.geocode_location("Boston", "US") is None


def test_fetch_current_weather_success(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")

    def fake_get(url, params, timeout):
        assert params["lat"] == 1.0
        assert params["lon"] == 2.0
        assert params["units"] == "metric"
        return DummyResponse(json_data={"weather": [], "main": {}}, text='{"ok":true}')

    monkeypatch.setattr(weather_api.requests, "get", fake_get)
    result = weather_api.fetch_current_weather(1.0, 2.0, "metric")
    assert isinstance(result, dict)


def test_fetch_current_weather_returns_none_without_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    assert weather_api.fetch_current_weather(1.0, 2.0, "metric") is None


def test_fetch_current_weather_returns_none_on_bad_json_shape(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")
    monkeypatch.setattr(
        weather_api.requests,
        "get",
        lambda url, params, timeout: DummyResponse(json_data=["not", "dict"], text="[]"),
    )
    assert weather_api.fetch_current_weather(1.0, 2.0, "metric") is None


def test_fetch_forecast_success(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")
    monkeypatch.setattr(
        weather_api.requests,
        "get",
        lambda url, params, timeout: DummyResponse(
            json_data={"list": [{"dt": 1}, {"dt": 2}]},
            text='{"list":[{"dt":1},{"dt":2}]}',
        ),
    )

    result = weather_api.fetch_forecast(1.0, 2.0, "metric")
    assert result == [{"dt": 1}, {"dt": 2}]


def test_fetch_forecast_returns_none_when_list_missing(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")
    monkeypatch.setattr(
        weather_api.requests,
        "get",
        lambda url, params, timeout: DummyResponse(json_data={"cod": 200}, text='{"cod":200}'),
    )

    assert weather_api.fetch_forecast(1.0, 2.0, "metric") is None


def test_fetch_forecast_returns_none_on_request_error(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key")

    def fake_get(url, params, timeout):
        raise weather_api.requests.RequestException("boom")

    monkeypatch.setattr(weather_api.requests, "get", fake_get)
    assert weather_api.fetch_forecast(1.0, 2.0, "metric") is None