from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, render_template, request
import os 
from services.weather_api import (
    geocode_location,
    fetch_current_weather,
    fetch_forecast,
)
from services.forecast_analyzer import (
    build_planner_insights,
    summarize_current_weather,
)
from utils.validators import normalize_units, validate_country_code
from utils.formatters import (
    format_current_payload,
    format_hourly_payload,
    format_daily_payload,
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/weather")
def get_weather():
    city = (request.args.get("city") or "").strip()
    country = (request.args.get("country") or "").strip().upper()
    units = normalize_units(request.args.get("units"))

    if not city:
        return jsonify({"error": "City is required."}), 400

    if country and not validate_country_code(country):
        return jsonify({"error": "Country must be a 2-letter code."}), 400

    location = geocode_location(city, country)
    if not location:
        return jsonify({"error": "Location not found."}), 404

    lat = location["lat"]
    lon = location["lon"]

    current = fetch_current_weather(lat, lon, units)
    forecast = fetch_forecast(lat, lon, units)

    if not current or not forecast:
        return jsonify({"error": "Weather data unavailable."}), 502

    current_payload = format_current_payload(current, units)
    hourly_payload = format_hourly_payload(forecast, units, limit=8)
    daily_payload = format_daily_payload(forecast, units, limit=5)
    insights = build_planner_insights(current_payload, hourly_payload)
    summary = summarize_current_weather(current_payload, insights)

    return jsonify(
        {
            "location": {
                "city": location.get("name", city),
                "country": location.get("country", country),
                "lat": lat,
                "lon": lon,
            },
            "current": current_payload,
            "hourly": hourly_payload,
            "daily": daily_payload,
            "insights": insights,
            "summary": summary,
        }
    )

@app.route("/test")
def test():
    return "test route works"


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5004)))