# 🌦️ Weather Window

A modern weather application that helps you **plan your day**, not just check the forecast.

Instead of only showing raw weather data, Weather Window provides **actionable insights** like:

* 🧥 What to wear
* 🌧️ Whether it will rain soon
* ⏰ Best time to go outside
* 😊 Comfort score based on conditions

## ✨ Features

* 🌍 Search weather by city and country
* 🌡️ Current weather conditions
* ⏳ Hourly forecast (next 24 hours)
* 📅 5-day forecast
* 🧠 Smart planner insights:

  * Best time to go out
  * Outfit recommendation
  * Rain prediction
  * Comfort score
* 🎨 Clean, modern UI (glassmorphism style)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pralfredo/weather_app.git
cd weather_app
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

You can get a free API key from:
👉 [https://openweathermap.org/api](https://openweathermap.org/api)

### 5. Run the app

```bash
python3 app.py
```

Open in your browser:

```text
http://127.0.0.1:5004
```

---

## 📂 Project Structure

```text
weather_app/
├── app.py
├── services/
│   ├── weather_api.py
│   └── forecast_analyzer.py
├── utils/
│   ├── validators.py
│   └── formatters.py
├── templates/
│   └── home.html
├── static/
│   ├── css/
│   └── js/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧠 How It Works

1. User inputs a city
2. App converts it to coordinates using geocoding
3. Fetches:

   * current weather
   * forecast data
4. Processes data into:

   * readable UI format
   * planner insights (best time, outfit, etc.)
5. Displays everything in a clean dashboard
