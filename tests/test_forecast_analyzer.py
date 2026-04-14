from services.forecast_analyzer import (
    build_planner_insights,
    calculate_comfort_score,
    find_best_time_window,
    recommend_outfit,
    summarize_current_weather,
    will_rain_soon,
)


def test_recommend_outfit_handles_none():
    assert recommend_outfit(None) == "Check conditions before heading out"


def test_recommend_outfit_cold():
    assert recommend_outfit(0) == "Heavy coat and warm layers"


def test_recommend_outfit_cool():
    assert recommend_outfit(10) == "Jacket or sweater"


def test_recommend_outfit_mild():
    assert recommend_outfit(18) == "Light layers"


def test_recommend_outfit_warm():
    assert recommend_outfit(24) == "T-shirt or breathable clothes"


def test_recommend_outfit_hot():
    assert recommend_outfit(32) == "Very light clothing and water"


def test_will_rain_soon_true():
    hourly = [
        {"pop": 10},
        {"pop": 40},
        {"pop": 0},
    ]
    assert will_rain_soon(hourly) is True


def test_will_rain_soon_false():
    hourly = [
        {"pop": 10},
        {"pop": 20},
        {"pop": 39},
    ]
    assert will_rain_soon(hourly) is False


def test_find_best_time_window_returns_unavailable_for_empty():
    assert find_best_time_window([]) == "Unavailable"


def test_find_best_time_window_prefers_best_score():
    hourly = [
        {"time_label": "9 AM", "temp": 10, "pop": 0},
        {"time_label": "3 PM", "temp": 21, "pop": 5},
        {"time_label": "6 PM", "temp": 19, "pop": 30},
    ]
    assert find_best_time_window(hourly) == "3 PM"


def test_find_best_time_window_skips_items_without_temp():
    hourly = [
        {"time_label": "9 AM", "pop": 0},
        {"time_label": "1 PM", "temp": 21, "pop": 0},
    ]
    assert find_best_time_window(hourly) == "1 PM"


def test_calculate_comfort_score_returns_default_when_temp_missing():
    assert calculate_comfort_score({}, []) == 50


def test_calculate_comfort_score_penalizes_rain():
    current = {"temp": 21, "humidity": 50, "wind_speed": 0}
    dry_hourly = [{"temp": 21, "pop": 0}]
    rainy_hourly = [{"temp": 21, "pop": 60}]
    assert calculate_comfort_score(current, rainy_hourly) < calculate_comfort_score(current, dry_hourly)


def test_calculate_comfort_score_stays_in_bounds():
    current = {"temp": -50, "humidity": 100, "wind_speed": 100}
    hourly = [{"temp": -50, "pop": 100}]
    score = calculate_comfort_score(current, hourly)
    assert 0 <= score <= 100


def test_build_planner_insights_shape():
    current = {
        "temp": 16,
        "condition": "Cloudy",
        "humidity": 60,
        "wind_speed": 3,
    }
    hourly = [
        {"time_label": "12 PM", "temp": 17, "pop": 10},
        {"time_label": "3 PM", "temp": 20, "pop": 5},
    ]
    insights = build_planner_insights(current, hourly)
    assert set(insights.keys()) == {"outfit", "best_time", "rain_soon", "comfort_score"}


def test_build_planner_insights_marks_rainy_condition():
    current = {
        "temp": 12,
        "condition": "Light rain",
        "humidity": 80,
        "wind_speed": 2,
    }
    hourly = [{"time_label": "3 PM", "temp": 12, "pop": 0}]
    insights = build_planner_insights(current, hourly)
    assert insights["rain_soon"] is True


def test_summarize_current_weather_contains_key_fields():
    current = {"temp": 12, "temp_unit": "°C", "condition": "Cloudy"}
    insights = {
        "best_time": "3 PM",
        "rain_soon": False,
        "outfit": "Jacket",
    }
    summary = summarize_current_weather(current, insights)
    assert "12°C" in summary
    assert "cloudy" in summary.lower()
    assert "3 PM" in summary
    assert "Jacket" in summary