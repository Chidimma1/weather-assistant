"""
test_calendar.py
Tests for the calendar_reader module.
File I/O is mocked — no real calendar.json required.
"""

import pytest
import json
import sys
import os
from datetime import datetime
from unittest.mock import patch, mock_open

# Make src/ importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from calendar_reader import load_events, _parse_events, _filter_today, CalendarEvent


# --- Sample event data ---
TODAY = datetime.now().date()
TODAY_STR = TODAY.strftime("%Y-%m-%d")

VALID_EVENTS = [
    {
        "title": "Morning Study Session",
        "start": f"{TODAY_STR}T08:00:00",
        "end": f"{TODAY_STR}T10:00:00",
        "location": "UH Library"
    },
    {
        "title": "Outdoor Networking Event",
        "start": f"{TODAY_STR}T16:00:00",
        "end": f"{TODAY_STR}T18:00:00",
        "location": "UH Cullen Lawn"
    }
]

FUTURE_EVENT = [
    {
        "title": "Next Week Meeting",
        "start": "2026-12-01T10:00:00",
        "end": "2026-12-01T11:00:00",
        "location": "Zoom"
    }
]

MALFORMED_EVENT = [
    {
        "title": "Missing Fields Event"
        # missing start, end, location
    }
]

INVALID_DATE_EVENT = [
    {
        "title": "Bad Date Event",
        "start": "not-a-date",
        "end": "also-not-a-date",
        "location": "Nowhere"
    }
]


# -------------------------------------------------------
# Tests for _parse_events()
# -------------------------------------------------------

def test_parse_events_returns_calendar_event_objects():
    """_parse_events() should return a list of CalendarEvent dataclasses."""
    result = _parse_events(VALID_EVENTS)

    assert len(result) == 2
    assert all(isinstance(e, CalendarEvent) for e in result)


def test_parse_events_correctly_maps_fields():
    """_parse_events() should correctly map title, start, end, and location."""
    result = _parse_events(VALID_EVENTS)

    assert result[0].title == "Morning Study Session"
    assert result[0].location == "UH Library"
    assert isinstance(result[0].start, datetime)
    assert isinstance(result[0].end, datetime)


def test_parse_events_skips_malformed_event_without_crashing():
    """_parse_events() should skip events with missing fields and not raise an error."""
    result = _parse_events(MALFORMED_EVENT)

    assert result == []


def test_parse_events_skips_invalid_date_without_crashing():
    """_parse_events() should skip events with unparseable dates and not raise an error."""
    result = _parse_events(INVALID_DATE_EVENT)

    assert result == []


def test_parse_events_returns_empty_list_for_empty_input():
    """_parse_events() should return an empty list when given an empty list."""
    result = _parse_events([])

    assert result == []


def test_parse_events_skips_bad_keeps_good():
    """_parse_events() should skip malformed events but still return valid ones."""
    mixed = VALID_EVENTS + MALFORMED_EVENT

    result = _parse_events(mixed)

    assert len(result) == 2


# -------------------------------------------------------
# Tests for _filter_today()
# -------------------------------------------------------

def test_filter_today_returns_only_todays_events():
    """_filter_today() should exclude events not scheduled for today."""
    all_events = _parse_events(VALID_EVENTS + FUTURE_EVENT)
    result = _filter_today(all_events)

    assert len(result) == 2
    assert all(e.start.date() == TODAY for e in result)


def test_filter_today_returns_empty_list_when_no_events_today():
    """_filter_today() should return an empty list if no events fall on today."""
    future_events = _parse_events(FUTURE_EVENT)
    result = _filter_today(future_events)

    assert result == []


def test_filter_today_handles_empty_input():
    """_filter_today() should return an empty list when given an empty list."""
    result = _filter_today([])

    assert result == []


# -------------------------------------------------------
# Tests for load_events() — file I/O mocked
# -------------------------------------------------------

def test_load_events_raises_file_not_found_when_missing():
    """load_events() should raise FileNotFoundError if calendar.json is missing."""
    with patch("calendar_reader.CALENDAR_FILE") as mock_path:
        mock_path.exists.return_value = False

        with pytest.raises(FileNotFoundError):
            load_events()


def test_load_events_raises_value_error_on_invalid_json():
    """load_events() should raise ValueError if calendar.json contains invalid JSON."""
    with patch("calendar_reader.CALENDAR_FILE") as mock_path:
        mock_path.exists.return_value = True
        with patch("builtins.open", mock_open(read_data="not valid json {")):
            with pytest.raises(ValueError):
                load_events()


def test_load_events_returns_only_todays_events_from_file():
    """load_events() should return only today's events from a valid calendar.json."""
    mock_data = json.dumps(VALID_EVENTS + FUTURE_EVENT)

    with patch("calendar_reader.CALENDAR_FILE") as mock_path:
        mock_path.exists.return_value = True
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = load_events()

    assert len(result) == 2
