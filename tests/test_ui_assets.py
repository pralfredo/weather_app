
from pathlib import Path


def test_home_template_includes_colorful_weather_platform_sections():
    template = Path("templates/home.html").read_text()
    assert "weather-map" in template
    assert "location-pill" in template
    assert "mapPrimaryMarker" in template
    assert "--night-1" in template
    assert "Open Map" in template


def test_app_javascript_updates_map_from_weather_response():
    script = Path("static/argon/js/app.js").read_text()
    assert "function updateMap" in script
    assert "openstreetmap.org" in script
    assert "conditionEmoji" in script
    assert "mapStatus.textContent" in script
