from typing import Dict, List, Optional

from calendar_reader import CalendarEvent
from weather import WeatherData, get_weather_at_hour

UMBRELLA_THRESHOLD = 50.0
HEAVY_RAIN_THRESHOLD = 80.0
HEAT_THRESHOLD = 95.0
COLD_THRESHOLD = 45.0
THUNDERSTORM_CODES = range(95, 100)
DEFAULT_ADVICE = "Weather looks good for this event. No special preparation needed."


def generate_advice(weather: WeatherData, events: List[CalendarEvent]) -> List[Dict[str, object]]:
    """Generate advice for each calendar event based on weather conditions."""
    advice_list: List[Dict[str, object]] = []
    for event in events:
        hour_conditions = get_weather_at_hour(weather, event.start.hour)
        recommendations = _apply_rules(hour_conditions)
        advice_list.append({"event": event, "advice": recommendations})
    return advice_list


def _apply_rules(conditions: Dict[str, float]) -> List[str]:
    """Apply advice rules to a set of weather conditions."""
    advice: List[str] = []
    for rule in (
        _check_thunderstorm,
        _check_heavy_rain,
        _check_moderate_rain,
        _check_extreme_heat,
        _check_cold,
    ):
        recommendation = rule(conditions)
        if recommendation:
            advice.append(recommendation)

    if not advice:
        advice.append(DEFAULT_ADVICE)

    return advice


def _check_thunderstorm(conditions: Dict[str, float]) -> Optional[str]:
    """Return thunderstorm advice when the weather code indicates severe storms."""
    weathercode = int(conditions.get("weathercode", 0))
    if weathercode in THUNDERSTORM_CODES:
        return "Thunderstorm conditions are expected. Stay under cover and avoid outdoor travel if possible."
    return None


def _check_heavy_rain(conditions: Dict[str, float]) -> Optional[str]:
    """Return heavy rain advice when precipitation probability is at least the heavy rain threshold."""
    precipitation = float(conditions.get("precipitation", 0.0))
    if precipitation >= HEAVY_RAIN_THRESHOLD:
        return "Heavy rain is forecast. Bring waterproof gear and expect wet conditions."
    return None


def _check_moderate_rain(conditions: Dict[str, float]) -> Optional[str]:
    """Return umbrella advice when precipitation probability is at least the umbrella threshold."""
    precipitation = float(conditions.get("precipitation", 0.0))
    if precipitation >= UMBRELLA_THRESHOLD:
        return "Moderate rain chance detected. Take an umbrella or rain jacket."
    return None


def _check_extreme_heat(conditions: Dict[str, float]) -> Optional[str]:
    """Return heat advice when temperature is at or above the heat threshold."""
    temperature = float(conditions.get("temperature", 0.0))
    if temperature >= HEAT_THRESHOLD:
        return "High temperatures are expected. Stay hydrated and avoid prolonged sun exposure."
    return None


def _check_cold(conditions: Dict[str, float]) -> Optional[str]:
    """Return cold weather advice when temperature is at or below the cold threshold."""
    temperature = float(conditions.get("temperature", 0.0))
    if temperature <= COLD_THRESHOLD:
        return "Cool weather is expected. Wear a jacket and warm layers."
    return None
