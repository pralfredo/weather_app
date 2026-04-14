const form = document.getElementById("weatherForm");
const cityInput = document.getElementById("city");
const countryInput = document.getElementById("country");
const unitsInput = document.getElementById("units");

const locationName = document.getElementById("locationName");
const summaryText = document.getElementById("summaryText");
const currentWeather = document.getElementById("currentWeather");
const insights = document.getElementById("insights");
const hourlyList = document.getElementById("hourlyList");
const dailyList = document.getElementById("dailyList");
const errorBox = document.getElementById("errorBox");

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
  return `https://openweathermap.org/img/wn/${icon}@2x.png`;
}

function clearWeatherCards() {
  currentWeather.innerHTML = "";
  insights.innerHTML = "";
  hourlyList.innerHTML = "";
  dailyList.innerHTML = "";
}

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

function renderWeather(data) {
  const { location, current, hourly, daily, insights: planner, summary } = data;

  locationName.textContent = `${location.city}${location.country ? ", " + location.country : ""}`;
  summaryText.textContent = summary;
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
        <span class="detail-value">${current.pressure}</span>
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
      <strong class="text-success">${planner.comfort_score}/100</strong>
    </div>
  `;

  hourlyList.innerHTML = hourly.map(item => `
    <div class="hour-card">
      <div class="hour-time">${item.time_label}</div>
      <img src="${weatherIconUrl(item.icon)}" alt="${item.condition}" width="56" height="56">
      <div class="hour-temp">${item.temp}${item.temp_unit}</div>
      <div class="hour-rain">${item.pop}%</div>
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
      <div class="day-rain">${item.pop}% rain</div>
    </div>
  `).join("");
}