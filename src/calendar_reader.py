"""
calendar_reader.py
Reads and parses calendar.json from the project root.
Returns only today's events as a list of CalendarEvent dataclasses.
"""

import json
import warnings
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path

CALENDAR_FILE = Path(__file__).parent.parent / "calendar.json"
REQUIRED_FIELDS = {"title", "start", "end", "location"}


@dataclass
class CalendarEvent:
    """Represents a single calendar event."""
    title: str
    start: datetime
    end: datetime
    location: str


def load_events() -> list:
    """Reads calendar.json and returns today's events."""
    if not CALENDAR_FILE.exists():
        raise FileNotFoundError(
            f"calendar.json not found at: {CALENDAR_FILE}\n"
            "Please create a calendar.json file in the project root."
        )
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            raw_events = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"calendar.json contains invalid JSON: {e}")

    parsed = _parse_events(raw_events)
    return _filter_today(parsed)


def _parse_events(raw_events: list) -> list:
    """Converts raw dicts into CalendarEvent dataclasses."""
    parsed = []
    for i, event in enumerate(raw_events):
        missing = REQUIRED_FIELDS - event.keys()
        if missing:
            warnings.warn("Skipping event with missing required fields")
            continue
        try:
            parsed.append(CalendarEvent(
                title=event["title"],
                start=datetime.fromisoformat(event["start"]),
                end=datetime.fromisoformat(event["end"]),
                location=event["location"]
            ))
        except ValueError:
            warnings.warn("Skipping event with invalid date format")
    return parsed


def _filter_today(events: list) -> list:
    """Returns only events scheduled for today."""
    today = date.today()
    return [e for e in events if e.start.date() == today]