import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Complete WMO Weather interpretation codes
WMO_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌧️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    56: "Light freezing drizzle 🌨️",
    57: "Dense freezing drizzle 🌨️",
    61: "Slight rain 🌦️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    66: "Light freezing rain 🌨️",
    67: "Heavy freezing rain 🌨️",
    71: "Slight snow 🌨️",
    73: "Moderate snow 🌨️",
    75: "Heavy snow ❄️",
    77: "Snow grains ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️",
    85: "Slight snow showers 🌨️",
    86: "Heavy snow showers ❄️",
    95: "Thunderstorm ⚡",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}

def get_weather_forecast(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time weather and today's forecast for a given city 
    using the completely free Open-Meteo API (no API key needed).
    """
    if not city_name or not city_name.strip():
        city_name = "New York"

    search_query = city_name.strip()

    try:
        # Step 1: Geocode city name to latitude & longitude
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = requests.get(geo_url, params={"name": search_query, "count": 1, "language": "en", "format": "json"}, timeout=8)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        # Fallback: if search_query has commas (e.g. "New Delhi, India"), try primary city part
        if not geo_data.get("results") and "," in search_query:
            fallback_city = search_query.split(",")[0].strip()
            geo_resp = requests.get(geo_url, params={"name": fallback_city, "count": 1, "language": "en", "format": "json"}, timeout=8)
            if geo_resp.status_code == 200:
                geo_data = geo_resp.json()

        if not geo_data.get("results"):
            logger.warning(f"Could not find coordinates for city: {city_name}")
            return None

        result = geo_data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        country = result.get("country_code", "")
        resolved_city = f"{result.get('name', search_query)}{', ' + country if country else ''}"

        # Step 2: Fetch forecast
        forecast_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
        }
        forecast_resp = requests.get(forecast_url, params=params, timeout=8)
        forecast_resp.raise_for_status()
        data = forecast_resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        current_code = current.get("weather_code", 0)
        condition = WMO_CODES.get(current_code, "Fair")

        temp = current.get("temperature_2m", "N/A")
        feels_like = current.get("apparent_temperature", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")

        temp_max_list = daily.get("temperature_2m_max") or []
        temp_min_list = daily.get("temperature_2m_min") or []
        rain_prob_list = daily.get("precipitation_probability_max") or []

        temp_max = temp_max_list[0] if temp_max_list else temp
        temp_min = temp_min_list[0] if temp_min_list else temp
        rain_prob = rain_prob_list[0] if rain_prob_list else "0"

        return {
            "city": resolved_city,
            "condition": condition,
            "current_temp": f"{temp}°C" if temp != "N/A" else "N/A",
            "feels_like": f"{feels_like}°C" if feels_like != "N/A" else "N/A",
            "temp_max": f"{temp_max}°C" if temp_max != "N/A" else "N/A",
            "temp_min": f"{temp_min}°C" if temp_min != "N/A" else "N/A",
            "humidity": f"{humidity}%" if humidity != "N/A" else "N/A",
            "wind_speed": f"{wind_speed} km/h" if wind_speed != "N/A" else "N/A",
            "rain_probability": f"{rain_prob}%" if rain_prob != "N/A" else "0%",
        }
    except Exception as e:
        logger.error(f"Error fetching weather data for {city_name}: {e}")
        return None
