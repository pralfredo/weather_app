const form = document.getElementById("weatherForm");
const cityInput = document.getElementById("city");
const countryInput = document.getElementById("country");
const unitsInput = document.getElementById("units");

const locationName = document.getElementById("locationName");
const locationPill = document.getElementById("locationPill");
const summaryText = document.getElementById("summaryText");
const currentTime = document.getElementById("currentTime");
const currentWeather = document.getElementById("currentWeather");
const insights = document.getElementById("insights");
const hourlyList = document.getElementById("hourlyList");
const dailyList = document.getElementById("dailyList");
const errorBox = document.getElementById("errorBox");
const mapPrimaryMarker = document.getElementById("mapPrimaryMarker");
const mapStatus = document.getElementById("mapStatus");
const mapLink = document.getElementById("mapLink");

function showError(message) {
  if (!errorBox) return;
  errorBox.textContent = message;
  errorBox.style.display = "block";
}

function clearError() {
  if (!errorBox) return;
  errorBox.textContent = "";
  errorBox.style.display = "none";
}

function weatherIconUrl(icon) {
  const safeIcon = icon || "01d";
  return `https://openweathermap.org/img/wn/${safeIcon}@2x.png`;
}

function currentTimeLabel() {
  return new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function conditionEmoji(condition = "") {
  const value = condition.toLowerCase();
  if (value.includes("thunder")) return "⛈️";
  if (value.includes("snow")) return "❄️";
  if (value.includes("rain") || value.includes("drizzle")) return "🌧️";
  if (value.includes("cloud")) return "☁️";
  if (value.includes("clear")) return "☀️";
  if (value.includes("mist") || value.includes("fog") || value.includes("haze")) return "🌫️";
  return "🌤️";
}

function clearWeatherCards() {
  if (currentWeather) currentWeather.innerHTML = "";
  if (insights) insights.innerHTML = "";
  if (hourlyList) hourlyList.innerHTML = "";
  if (dailyList) dailyList.innerHTML = "";
}

function updateMap(location, current) {
  if (!location || !mapPrimaryMarker) return;

  const lat = Number(location.lat);
  const lon = Number(location.lon);
  const x = Number.isFinite(lon) ? Math.min(88, Math.max(12, ((lon + 180) / 360) * 100)) : 50;
  const y = Number.isFinite(lat) ? Math.min(84, Math.max(16, ((90 - lat) / 180) * 100)) : 48;
  const place = `${location.city}${location.country ? ", " + location.country : ""}`;

  mapPrimaryMarker.style.left = `${x}%`;
  mapPrimaryMarker.style.top = `${y}%`;
  mapPrimaryMarker.innerHTML = `
    <span class="marker-icon">${conditionEmoji(current.condition)}</span>
    <span>${place}</span>
    <span>${current.temp}${current.temp_unit}</span>
  `;

  if (mapStatus) {
    mapStatus.textContent = current.condition.toLowerCase().includes("rain")
      ? "Precipitation is active near this location"
      : "No precipitation for at least the next few hours";
  }

  if (mapLink && Number.isFinite(lat) && Number.isFinite(lon)) {
    mapLink.href = `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=8/${lat}/${lon}`;
  }
}

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    const city = cityInput.value.trim();
    const country = countryInput.value.trim();
    const units = unitsInput.value;

    if (!city) {
      showError("Please enter a city.");
      return;
    }

    locationName.textContent = "Loading...";
    summaryText.textContent = "Fetching weather data...";
    if (currentTime) currentTime.textContent = currentTimeLabel();
    clearWeatherCards();

    const params = new URLSearchParams({ city, units });
    if (country) params.set("country", country);

    try {
      const response = await fetch(`/api/weather?${params.toString()}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
      }

      renderWeather(data);
    } catch (error) {
      locationName.textContent = "Error";
      summaryText.textContent = error.message;
      showError(error.message);
      clearWeatherCards();
    }
  });
}

function renderWeather(data) {
  const { location, current, hourly, daily, insights: planner, summary } = data;
  const displayLocation = `${location.city}${location.country ? ", " + location.country : ""}`;

  locationName.textContent = displayLocation;
  summaryText.textContent = summary;
  if (locationPill) {
    locationPill.innerHTML = `
      <i class="fa-solid fa-location-dot"></i>
      <span>${displayLocation}</span>
      <i class="fa-solid fa-chevron-down text-xs"></i>
    `;
  }
  if (currentTime) currentTime.textContent = currentTimeLabel();
  clearError();

  currentWeather.innerHTML = `
    <div class="current-main-row">
      <div class="current-icon-wrap">
        <img class="weather-big-icon" src="${weatherIconUrl(current.icon)}" alt="${current.condition}">
      </div>

      <div class="current-temp-wrap">
        <div class="current-temp-value">${current.temp}${current.temp_unit}</div>
      </div>

      <div class="current-desc-wrap">
        <div class="current-condition">${current.condition}</div>
        <div class="current-feels">Feels like ${current.feels_like}${current.temp_unit}</div>
      </div>
    </div>

    <div class="current-summary">${summary}</div>

    <div class="details-grid">
      <div class="detail-item">
        <span class="detail-label">Wind</span>
        <span class="detail-value">${current.wind_speed} ${current.wind_unit}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Humidity</span>
        <span class="detail-value">${current.humidity}%</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Visibility</span>
        <span class="detail-value">${current.visibility}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Pressure</span>
        <span class="detail-value">${current.pressure} mb</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Sunrise</span>
        <span class="detail-value">${current.sunrise}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Sunset</span>
        <span class="detail-value">${current.sunset}</span>
      </div>
    </div>
  `;

  insights.innerHTML = `
    <div class="metric-row">
      <span class="text-sm text-secondary">Best time to go out</span>
      <strong>${planner.best_time}</strong>
    </div>
    <div class="metric-row">
      <span class="text-sm text-secondary">Outfit</span>
      <strong>${planner.outfit}</strong>
    </div>
    <div class="metric-row">
      <span class="text-sm text-secondary">Rain soon</span>
      <strong>${planner.rain_soon ? "Yes" : "No"}</strong>
    </div>
    <div class="metric-row">
      <span class="text-sm text-secondary">Comfort score</span>
      <strong>${planner.comfort_score}/100</strong>
    </div>
  `;

  hourlyList.innerHTML = hourly.map(item => `
    <div class="hour-card">
      <div class="hour-time">${item.time_label}</div>
      <img src="${weatherIconUrl(item.icon)}" alt="${item.condition}" width="56" height="56">
      <div class="hour-temp">${item.temp}${item.temp_unit}</div>
      <div class="hour-rain">💧 ${item.pop}%</div>
    </div>
  `).join("");

  dailyList.innerHTML = daily.map((item, index) => `
    <div class="day-card ${index === 0 ? "day-card-featured" : ""}">
      <div class="day-name">${index === 0 ? "Tonight" : item.date_label}</div>
      <img src="${weatherIconUrl(item.icon)}" alt="${item.condition}" width="60" height="60">
      <div class="day-temps">
        <span>${item.temp_max}${item.temp_unit}</span>
        <span class="day-temp-low">${item.temp_min}${item.temp_unit}</span>
      </div>
      <div class="day-desc">${item.condition}</div>
      <div class="day-rain">💧 ${item.pop}%</div>
    </div>
  `).join("");

  updateMap(location, current);
}
