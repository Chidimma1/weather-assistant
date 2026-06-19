"""
test_weather.py
Tests for the weather module.
API calls are mocked — no real internet connection required.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import date
import sys
import os

# Make src/ importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from weather import fetch_weather, get_weather_at_hour, WeatherData, _parse_response


# --- Sample mock API response ---
MOCK_API_RESPONSE = {
    "hourly": {
        "temperature_2m": [75.0] * 24,
        "precipitation_probability": [10.0] * 24,
        "weathercode": [0] * 24
    }
}


# -------------------------------------------------------
# Tests for fetch_weather()
# -------------------------------------------------------

@patch("weather.requests.get")
def test_fetch_weather_returns_weather_data(mock_get):
    """fetch_weather() should return a WeatherData object on success."""
    mock_response = Mock()
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = fetch_weather()

    assert isinstance(result, WeatherData)


@patch("weather.requests.get")
def test_fetch_weather_date_is_today(mock_get):
    """fetch_weather() should set the date field to today."""
    mock_response = Mock()
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = fetch_weather()

    assert result.date == date.today()


@patch("weather.requests.get")
def test_fetch_weather_returns_24_hourly_values(mock_get):
    """fetch_weather() should return 24 values for each hourly field."""
    mock_response = Mock()
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = fetch_weather()

    assert len(result.hourly_temperature) == 24
    assert len(result.hourly_precipitation) == 24
    assert len(result.hourly_weathercode) == 24


@patch("weather.requests.get")
def test_fetch_weather_raises_connection_error_on_network_failure(mock_get):
    """fetch_weather() should raise ConnectionError if the API is unreachable."""
    import requests as req
    mock_get.side_effect = req.exceptions.ConnectionError

    with pytest.raises(ConnectionError):
        fetch_weather()


@patch("weather.requests.get")
def test_fetch_weather_raises_connection_error_on_timeout(mock_get):
    """fetch_weather() should raise ConnectionError if the request times out."""
    import requests as req
    mock_get.side_effect = req.exceptions.Timeout

    with pytest.raises(ConnectionError):
        fetch_weather()


# -------------------------------------------------------
# Tests for _parse_response()
# -------------------------------------------------------

def test_parse_response_raises_value_error_on_missing_field():
    """_parse_response() should raise ValueError if API response is malformed."""
    bad_response = {"hourly": {"temperature_2m": [75.0] * 24}}  # missing fields

    with pytest.raises(ValueError):
        _parse_response(bad_response)


# -------------------------------------------------------
# Tests for get_weather_at_hour()
# -------------------------------------------------------

def test_get_weather_at_hour_returns_correct_values():
    """get_weather_at_hour() should return the correct values for the given hour."""
    weather = WeatherData(
        hourly_temperature=[60.0 + i for i in range(24)],
        hourly_precipitation=[i * 2.0 for i in range(24)],
        hourly_weathercode=[0] * 24,
        date=date.today()
    )

    result = get_weather_at_hour(weather, 10)

    assert result["temperature"] == 70.0
    assert result["precipitation"] == 20.0
    assert result["weathercode"] == 0


def test_get_weather_at_hour_returns_dict_with_correct_keys():
    """get_weather_at_hour() should always return a dict with the three expected keys."""
    weather = WeatherData(
        hourly_temperature=[75.0] * 24,
        hourly_precipitation=[30.0] * 24,
        hourly_weathercode=[1] * 24,
        date=date.today()
    )

    result = get_weather_at_hour(weather, 0)

    assert "temperature" in result
    assert "precipitation" in result
    assert "weathercode" in result
