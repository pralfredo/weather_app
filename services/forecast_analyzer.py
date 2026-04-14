def build_planner_insights(current: dict, hourly: list[dict]) -> dict:
    temp = current.get("temp")
    condition = (current.get("condition") or "").lower()
    is_rainy_now = "rain" in condition or "drizzle" in condition

    outfit = recommend_outfit(temp)
    best_time = find_best_time_window(hourly)
    rain_soon = will_rain_soon(hourly) or is_rainy_now
    comfort_score = calculate_comfort_score(current, hourly)

    return {
        "outfit": outfit,
        "best_time": best_time,
        "rain_soon": rain_soon,
        "comfort_score": comfort_score,
    }


def summarize_current_weather(current: dict, insights: dict) -> str:
    temp = current.get("temp")
    unit = current.get("temp_unit", "")
    condition = (current.get("condition") or "Unknown").lower()

    rain_text = "Rain is possible soon." if insights["rain_soon"] else "Rain is not likely soon."
    return (
        f"It is currently {temp}{unit} with {condition}. "
        f"Best time to go out: {insights['best_time']}. "
        f"{rain_text} Suggested outfit: {insights['outfit']}."
    )


def recommend_outfit(temp: float | None) -> str:
    if temp is None:
        return "Check conditions before heading out"

    if temp < 5:
        return "Heavy coat and warm layers"
    if temp < 12:
        return "Jacket or sweater"
    if temp < 20:
        return "Light layers"
    if temp < 28:
        return "T-shirt or breathable clothes"
    return "Very light clothing and water"


def will_rain_soon(hourly: list[dict]) -> bool:
    for item in hourly[:3]:
        if item.get("pop", 0) >= 40:
            return True
    return False


def find_best_time_window(hourly: list[dict]) -> str:
    if not hourly:
        return "Unavailable"

    best_item = None
    best_score = float("-inf")

    for item in hourly:
        temp = item.get("temp")
        pop = item.get("pop", 0)

        if temp is None:
            continue

        score = 100
        score -= abs(temp - 21) * 2
        score -= pop * 1.2

        if score > best_score:
            best_score = score
            best_item = item

    if not best_item:
        return "Unavailable"

    return best_item.get("time_label", "Unavailable")


def calculate_comfort_score(current: dict, hourly: list[dict]) -> int:
    temp = current.get("temp")
    humidity = current.get("humidity", 50)
    wind = current.get("wind_speed", 0)

    if temp is None:
        return 50

    score = 100
    score -= min(abs(temp - 21) * 2, 40)
    score -= min(abs(humidity - 50) * 0.3, 15)
    score -= min(wind * 0.8, 20)

    if will_rain_soon(hourly):
        score -= 15

    return max(0, min(100, round(score)))