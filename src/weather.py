from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List

import requests


@dataclass
class WeatherData:
    """Hourly weather data for a single date."""

    hourly_temperature: List[float]
    hourly_precipitation: List[float]
    hourly_weathercode: List[int]
    date: date


def fetch_weather() -> WeatherData:
    """Fetch today\'s hourly weather forecast for Houston, TX from Open-Meteo."""
    latitude = 29.7604
    longitude = -95.3698
    today = date.today().isoformat()
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation_probability,weathercode",
        "temperature_unit": "fahrenheit",
        "timezone": "America/Chicago",
        "start_date": today,
        "end_date": today,
    }
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return _parse_response(response.json())
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
        raise ConnectionError("Unable to fetch weather data") from exc


def _parse_response(data: Dict[str, Any]) -> WeatherData:
    """Parse the Open-Meteo API response into a WeatherData object."""
    hourly = data.get("hourly")
    if not isinstance(hourly, dict):
        raise ValueError("Missing hourly weather data in API response")

    temperature_values = hourly.get("temperature_2m")
    precipitation_values = hourly.get("precipitation_probability")
    weathercode_values = hourly.get("weathercode")
    if (
        temperature_values is None
        or precipitation_values is None
        or weathercode_values is None
    ):
        raise ValueError("API response is missing required hourly fields")

    if not (
        isinstance(temperature_values, list)
        and isinstance(precipitation_values, list)
        and isinstance(weathercode_values, list)
    ):
        raise ValueError("Hourly fields must be lists")

    if not (
        len(temperature_values) == len(precipitation_values) == len(weathercode_values)
    ):
        raise ValueError("Hourly fields must contain the same number of values")

    return WeatherData(
        hourly_temperature=[float(value) for value in temperature_values],
        hourly_precipitation=[float(value) for value in precipitation_values],
        hourly_weathercode=[int(value) for value in weathercode_values],
        date=date.today(),
    )


def get_weather_at_hour(weather: WeatherData, hour: int) -> Dict[str, Any]:
    """Return the weather values for a specific hour from WeatherData."""
    return {
        "temperature": weather.hourly_temperature[hour],
        "precipitation": weather.hourly_precipitation[hour],
        "weathercode": weather.hourly_weathercode[hour],
    }
