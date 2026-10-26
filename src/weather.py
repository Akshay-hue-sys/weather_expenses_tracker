from typing import Optional
import httpx
from projects.weather_expense_tracker.src.schemas import WeatherInfo

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def fetch_current_weather(
    latitude: float,
    longitude: float,
    timeout_seconds: float = 5.0,
) -> Optional[WeatherInfo]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
    }
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(OPEN_METEO_FORECAST_URL, params=params)
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})
            return WeatherInfo(
                temperature_c=current["temperature_2m"],
                weather_code=current["weather_code"],
                wind_speed_kmh=current["wind_speed_10m"],
            )
    except (httpx.HTTPError, KeyError, ValueError):
        return None


async def search_weather_by_name(
    query: str,
    timeout_seconds: float = 5.0,
) -> Optional[dict]:
    params = {"name": query, "count": 1, "language": "en", "format": "json"}
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            geo_response = await client.get(OPEN_METEO_GEOCODING_URL, params=params)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            results = geo_data.get("results")
            if not results:
                return None

            top_match = results[0]
            lat = top_match["latitude"]
            lon = top_match["longitude"]
            place_label = f"{top_match.get('name')}, {top_match.get('admin1', '')} ({top_match.get('country', '')})"

            weather = await fetch_current_weather(
                latitude=lat,
                longitude=lon,
                timeout_seconds=timeout_seconds,
            )
            if weather is None:
                return None

            return {
                "location": place_label,
                "latitude": lat,
                "longitude": lon,
                "weather": weather,
            }
    except (httpx.HTTPError, KeyError, ValueError):
        return None