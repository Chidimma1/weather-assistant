"""
test_advisor.py
Tests for the advisor module.
Covers all advice rules R-1 through R-6 from the PRD.
All weather data is mocked — no API calls made.
"""

import pytest
import sys
import os
from datetime import datetime, date

# Make src/ importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from advisor import generate_advice, _apply_rules
from weather import WeatherData
from calendar_reader import CalendarEvent


# -------------------------------------------------------
# Helpers — build mock data quickly
# -------------------------------------------------------

def make_weather(temperature=75.0, precipitation=10.0, weathercode=0) -> WeatherData:
    """
    Creates a WeatherData object with uniform values across all 24 hours.
    Makes it easy to test specific conditions without building 24-item lists manually.
    """
    return WeatherData(
        hourly_temperature=[temperature] * 24,
        hourly_precipitation=[precipitation] * 24,
        hourly_weathercode=[weathercode] * 24,
        date=date.today()
    )


def make_event(title="Test Event", hour=10, location="Test Location") -> CalendarEvent:
    """
    Creates a CalendarEvent starting at the given hour today.
    """
    today = date.today()
    return CalendarEvent(
        title=title,
        start=datetime(today.year, today.month, today.day, hour, 0),
        end=datetime(today.year, today.month, today.day, hour + 1, 0),
        location=location
    )


# -------------------------------------------------------
# Tests for Rule R-1 — Moderate Rain (precipitation >= 50%)
# -------------------------------------------------------

def test_r1_umbrella_advice_triggered_when_precipitation_above_50():
    """R-1: Umbrella advice should fire when precipitation probability >= 50%."""
    conditions = {"temperature": 75.0, "precipitation": 55.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("umbrella" in line.lower() for line in result)


def test_r1_umbrella_advice_triggered_at_exactly_50():
    """R-1: Umbrella advice should fire at exactly 50% precipitation."""
    conditions = {"temperature": 75.0, "precipitation": 50.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("umbrella" in line.lower() for line in result)


def test_r1_umbrella_advice_not_triggered_below_50():
    """R-1: Umbrella advice should NOT fire when precipitation is below 50%."""
    conditions = {"temperature": 75.0, "precipitation": 49.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert not any("umbrella" in line.lower() for line in result)


# -------------------------------------------------------
# Tests for Rule R-2 — Heavy Rain (precipitation >= 80%)
# -------------------------------------------------------

def test_r2_heavy_rain_advice_triggered_when_precipitation_above_80():
    """R-2: Heavy rain advice should fire when precipitation probability >= 80%."""
    conditions = {"temperature": 75.0, "precipitation": 85.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("heavy rain" in line.lower() for line in result)


def test_r2_heavy_rain_also_triggers_r1_umbrella():
    """R-2 + R-1: When precipitation >= 80%, both heavy rain AND umbrella advice should fire."""
    conditions = {"temperature": 75.0, "precipitation": 85.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("heavy rain" in line.lower() for line in result)
    assert any("umbrella" in line.lower() for line in result)


def test_r2_heavy_rain_not_triggered_below_80():
    """R-2: Heavy rain advice should NOT fire when precipitation is below 80%."""
    conditions = {"temperature": 75.0, "precipitation": 75.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert not any("heavy rain" in line.lower() for line in result)


# -------------------------------------------------------
# Tests for Rule R-3 — Extreme Heat (temperature >= 95°F)
# -------------------------------------------------------

def test_r3_heat_advice_triggered_when_temperature_above_95():
    """R-3: Heat advice should fire when temperature >= 95°F."""
    conditions = {"temperature": 98.0, "precipitation": 5.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("hydrated" in line.lower() for line in result)


def test_r3_heat_advice_triggered_at_exactly_95():
    """R-3: Heat advice should fire at exactly 95°F."""
    conditions = {"temperature": 95.0, "precipitation": 5.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("hydrated" in line.lower() for line in result)


def test_r3_heat_advice_not_triggered_below_95():
    """R-3: Heat advice should NOT fire when temperature is below 95°F."""
    conditions = {"temperature": 94.0, "precipitation": 5.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert not any("hydrated" in line.lower() for line in result)


# -------------------------------------------------------
# Tests for Rule R-4 — Cold Weather (temperature <= 45°F)
# -------------------------------------------------------

def test_r4_cold_advice_triggered_when_temperature_below_45():
    """R-4: Cold advice should fire when temperature <= 45°F."""
    conditions = {"temperature": 40.0, "precipitation": 5.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("jacket" in line.lower() for line in result)


def test_r4_cold_advice_triggered_at_exactly_45():
    """R-4: Cold advice should fire at exactly 45°F."""
    conditions = {"temperature": 45.0, "precipitation": 5.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("jacket" in line.lower() for line in result)


def test_r4_cold_advice_not_triggered_above_45():
    """R-4: Cold advice should NOT fire when temperature is above 45°F."""
    conditions = {"temperature": 46.0, "precipitation": 5.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert not any("jacket" in line.lower() for line in result)


# -------------------------------------------------------
# Tests for Rule R-5 — Thunderstorm (WMO codes 95–99)
# -------------------------------------------------------

def test_r5_thunderstorm_advice_triggered_for_weathercode_95():
    """R-5: Thunderstorm advice should fire for WMO code 95."""
    conditions = {"temperature": 75.0, "precipitation": 70.0, "weathercode": 95}

    result = _apply_rules(conditions)

    assert any("thunderstorm" in line.lower() for line in result)


def test_r5_thunderstorm_advice_triggered_for_weathercode_99():
    """R-5: Thunderstorm advice should fire for WMO code 99."""
    conditions = {"temperature": 75.0, "precipitation": 70.0, "weathercode": 99}

    result = _apply_rules(conditions)

    assert any("thunderstorm" in line.lower() for line in result)


def test_r5_thunderstorm_advice_not_triggered_for_clear_code():
    """R-5: Thunderstorm advice should NOT fire for clear sky WMO code 0."""
    conditions = {"temperature": 75.0, "precipitation": 10.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert not any("thunderstorm" in line.lower() for line in result)


# -------------------------------------------------------
# Tests for Rule R-6 — Clear Weather (no conditions triggered)
# -------------------------------------------------------

def test_r6_clear_advice_returned_when_no_rules_fire():
    """R-6: Clear weather message should appear when no other rules are triggered."""
    conditions = {"temperature": 75.0, "precipitation": 10.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert any("no special preparation" in line.lower() for line in result)


def test_r6_clear_advice_not_returned_when_other_rules_fire():
    """R-6: Clear weather message should NOT appear when other rules are triggered."""
    conditions = {"temperature": 75.0, "precipitation": 60.0, "weathercode": 0}

    result = _apply_rules(conditions)

    assert not any("no special preparation" in line.lower() for line in result)


# -------------------------------------------------------
# Tests for generate_advice() — end-to-end advisor logic
# -------------------------------------------------------

def test_generate_advice_returns_one_result_per_event():
    """generate_advice() should return exactly one result dict per event."""
    weather = make_weather(precipitation=10.0)
    events = [make_event("Event A"), make_event("Event B")]

    result = generate_advice(weather, events)

    assert len(result) == 2


def test_generate_advice_result_contains_event_and_advice_keys():
    """generate_advice() results should have 'event' and 'advice' keys."""
    weather = make_weather()
    events = [make_event()]

    result = generate_advice(weather, events)

    assert "event" in result[0]
    assert "advice" in result[0]


def test_generate_advice_returns_empty_list_for_no_events():
    """generate_advice() should return an empty list when no events are provided."""
    weather = make_weather()

    result = generate_advice(weather, [])

    assert result == []


def test_generate_advice_rain_event_gets_umbrella_advice():
    """generate_advice() should give umbrella advice for an event during rainy weather."""
    weather = make_weather(precipitation=60.0)
    events = [make_event("Outdoor Meeting", hour=14)]

    result = generate_advice(weather, events)

    assert any("umbrella" in line.lower() for line in result[0]["advice"])
