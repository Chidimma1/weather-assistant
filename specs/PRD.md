# Product Requirements Document (PRD)
# Weather-Aware Personal Assistant

**Author:** Chidimma Ukoha
**Course:** Generative AI — Self Discovery Lab
**Version:** 1.0
**Date:** June 2026
**Status:** Final

---

## 1. Overview

The Weather-Aware Personal Assistant is a CLI-based (REPL) tool that combines real-time weather data with a user's local schedule to generate plain-English, context-aware daily advice. The assistant reads the user's calendar, checks the weather for each event's location, and tells the user what to expect and how to prepare — all in one command.

---

## 2. Problem Statement

People plan their day in silos: they check the weather in one app and their calendar in another, and they mentally connect the dots themselves. This works until it doesn't — they show up to an outdoor meeting in the rain without an umbrella, or wear a coat to a noon lunch on a sunny 90°F Houston day.

This assistant eliminates that mental overhead by doing the synthesis automatically.

---

## 3. Target User

A graduate student or working professional based in Houston, TX who maintains a lightweight local schedule and wants a single-command morning briefing that tells them what to wear, what to bring, and how to get to their events — given today's weather.

---

## 4. Goals

| Goal | Description |
|------|-------------|
| G-1 | Fetch real-time weather data for the user's city without requiring an API key |
| G-2 | Read and parse a local `calendar.json` file containing today's events |
| G-3 | Generate plain-English advice per event based on weather conditions |
| G-4 | Run entirely from the command line with a single command: `python src/main.py` |
| G-5 | Be fully testable — core logic must work independent of the CLI and API |

---

## 5. Non-Goals

- No graphical user interface (GUI)
- No user authentication or login
- No database — `calendar.json` is the only data store
- No support for multiple users or user profiles
- No push notifications or scheduling of runs (user runs it manually)
- No natural language input from the user

---

## 6. Core Features

### Feature 1 — Weather Fetching (`src/weather.py`)
- Fetch today's hourly weather forecast for Houston, TX using the [Open-Meteo API](https://open-meteo.com/)
- No API key required
- Extract the following fields for each hour:
  - `temperature_2m` (°F)
  - `precipitation_probability` (%)
  - `weathercode` (WMO weather interpretation code)
- Return a structured `WeatherData` dataclass

### Feature 2 — Calendar Reading (`src/calendar_reader.py`)
- Read `calendar.json` from the project root
- Parse each event's `start` and `end` as ISO 8601 datetime strings
- Filter to return only **today's** events
- Return a list of `CalendarEvent` dataclasses
- Handle gracefully: file not found, empty list, malformed JSON

### Feature 3 — Advice Engine (`src/advisor.py`)
- Accept a `WeatherData` object and a list of `CalendarEvent` objects
- Match each event's time window to the corresponding hourly weather forecast
- Apply rule-based logic to generate advice strings (see Section 7)
- Return a list of plain-English advice strings — one per event
- **No print statements inside this module**

### Feature 4 — CLI Entry Point (`src/main.py`)
- Orchestrate calls to the three modules above
- Print the final advice to the terminal in a clean, readable format
- This file contains **only** wiring and print statements — zero business logic

---

## 7. Advice Logic (Rule-Based)

The advisor applies these rules in order. Multiple rules can fire for one event.

| Rule ID | Condition | Advice Output |
|---------|-----------|---------------|
| R-1 | `precipitation_probability >= 50%` | "Bring an umbrella or consider taking the bus." |
| R-2 | `precipitation_probability >= 80%` | "Heavy rain likely — strongly consider rescheduling or going fully remote." |
| R-3 | `temperature >= 95°F` | "Extreme heat expected — stay hydrated and wear light clothing." |
| R-4 | `temperature <= 45°F` | "It will be cold — wear a jacket." |
| R-5 | `weathercode` indicates thunderstorm (WMO codes 95–99) | "Thunderstorms forecast — avoid outdoor locations if possible." |
| R-6 | No triggering conditions | "Weather looks good for this event. No special preparation needed." |

Rules R-1 and R-2 are cumulative: if precipitation is ≥ 80%, both R-1 and R-2 fire.

---

## 8. Data Contracts

### `calendar.json` Schema

The file lives in the project root. It is an array of event objects. Minimum required fields:

```json
[
  {
    "title": "string — name of the event",
    "start": "ISO 8601 datetime — e.g. 2026-06-19T10:00:00",
    "end":   "ISO 8601 datetime — e.g. 2026-06-19T12:00:00",
    "location": "string — Location"
  }
]
```

**Constraints:**
- `title` and `location` are required strings
- `start` and `end` must be valid ISO 8601 datetime strings
- Events with missing required fields are skipped with a warning, not a crash

---

### `WeatherData` Dataclass

```python
@dataclass
class WeatherData:
    hourly_temperature: list[float]   # one value per hour, index 0 = midnight
    hourly_precipitation: list[float] # precipitation probability per hour (0–100)
    hourly_weathercode: list[int]     # WMO weather code per hour
    date: date                        # the date this forecast is for
```

---

### `CalendarEvent` Dataclass

```python
@dataclass
class CalendarEvent:
    title: str
    start: datetime
    end: datetime
    location: str
```

---

## 9. Folder Structure

```
weather-assistant/
├── specs/
│   └── PRD.md                  ← This document
├── docs/
│   └── rules.md                ← AI agent persona and coding constraints
├── src/
│   ├── main.py                 ← CLI entry point (wiring + print only)
│   ├── weather.py              ← Fetches weather from Open-Meteo API
│   ├── calendar_reader.py      ← Reads and parses calendar.json
│   └── advisor.py              ← Rule-based advice engine
├── tests/
│   ├── test_weather.py         ← Tests for weather module
│   ├── test_calendar.py        ← Tests for calendar reader
│   └── test_advisor.py         ← Tests for advice logic (core rubric target)
├── calendar.json               ← User's local schedule (created manually)
├── requirements.txt            ← Python dependencies
└── README.md                   ← Setup instructions + Vibe Report
```

---

## 10. Success Criteria

The app is considered complete when ALL of the following are true:

- [ ] `python src/main.py` runs without errors
- [ ] Weather data is fetched live from Open-Meteo for today's date
- [ ] Only today's events are returned from `calendar.json`
- [ ] At least one piece of advice is generated per event
- [ ] All tests in `tests/` pass via `pytest`
- [ ] Rule R-1 is covered by a test with a mocked weather input of precipitation ≥ 50%
- [ ] Rule R-6 (clear weather) is covered by a test with precipitation < 20%
- [ ] `advisor.py` contains zero `print()` calls
- [ ] `main.py` contains zero business logic

---

## 11. Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Language | Python 3.11+ | Standard for data/AI coursework |
| Weather API | Open-Meteo (free, no key) | Zero friction, reliable |
| Data parsing | Python `dataclasses` + `datetime` stdlib | No extra dependencies |
| HTTP requests | `requests` library | Simple and readable |
| Testing | `pytest` | Industry standard |
| CLI | Plain `python src/main.py` | Keeps scope tight |

---

## 12. Out of Scope for v1.0 (Future Enhancements)

- LLM-powered advice (GPT/Claude integration) — rule-based is sufficient for v1
- Multi-city support — Houston only for v1
- `.env` config for user preferences
- Google Calendar or iCal integration

---

*This PRD is the source of truth. The AI agent will be instructed to implement exactly what is written here — no more, no less.*
