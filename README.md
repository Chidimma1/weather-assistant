# 🌤 Weather-Aware Personal Assistant

A CLI-based personal assistant that fetches real-time weather data and combines
it with your local schedule to generate plain-English, context-aware daily advice.

**Course:** Generative AI — Self Discovery Lab
**Author:** Chidimma
**University:** University of Houston — Cullen College of Engineering
**Program:** M.S. Engineering Data Science & AI

---

## 📋 What It Does

Run one command every morning and get a personalized daily briefing like this:

```
=======================================================
   🌤  Weather-Aware Personal Assistant
=======================================================

📡 Fetching today's weather for Houston, TX...
✅ Weather data loaded.

📅 Reading your calendar...
✅ Found 6 event(s) for today.

=======================================================
   📋 Your Daily Briefing
=======================================================

🗓  Morning Study Session
    🕐 08:00 AM – 10:00 AM
    📍 UH MD Anderson Library
    💬 Advice:
       • Weather looks good for this event. No special preparation needed.

🗓  Outdoor Networking Event
    🕐 04:00 PM – 06:00 PM
    📍 UH Cullen Performance Hall Lawn
    💬 Advice:
       • ☂ Bring an umbrella or consider taking the bus.
       • 🥵 Extreme heat expected — stay hydrated and wear light clothing.
```

---

## 🗂 Project Structure

```
weather-assistant/
├── specs/
│   └── PRD.md                  ← Product Requirements Document (source of truth)
├── docs/
│   └── rules.md                ← AI agent persona and coding constraints
├── src/
│   ├── main.py                 ← CLI entry point (wiring + print only)
│   ├── weather.py              ← Fetches weather from Open-Meteo API
│   ├── calendar_reader.py      ← Reads and parses calendar.json
│   └── advisor.py              ← Rule-based advice engine
├── tests/
│   ├── test_advisor.py         ← 21 tests covering all advice rules R-1 to R-6
│   ├── test_calendar.py        ← 13 tests for calendar parsing and filtering
│   └── test_weather.py         ← 7 tests for weather fetching and parsing
├── calendar.json               ← Your local schedule (edit this with your events)
├── requirements.txt            ← Python dependencies
└── README.md                   ← This file
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11 or higher
- pip

### Step 1 — Clone the repository
```bash
git clone https://github.com/Chidimma1/weather-assistant.git
cd weather-assistant
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Edit your calendar
Open `calendar.json` and replace the sample events with your own schedule.
Each event must follow this structure:
```json
{
  "title": "Your Event Name",
  "start": "2026-06-18T10:00:00",
  "end": "2026-06-18T12:00:00",
  "location": "Your Location"
}
```

### Step 4 — Run the assistant
```bash
python src/main.py
```

### Step 5 — Run the tests
```bash
pytest tests/ -v
```

---

## 🌐 Weather API

This app uses [Open-Meteo](https://open-meteo.com/) — a free, open-source
weather API that requires **no API key**. Data is fetched for Houston, TX
(latitude: 29.7604, longitude: -95.3698).

---

## 💬 Advice Rules

| Rule | Condition | Advice |
|------|-----------|--------|
| R-1 | Precipitation ≥ 50% | Bring an umbrella or take the bus |
| R-2 | Precipitation ≥ 80% | Heavy rain — consider rescheduling |
| R-3 | Temperature ≥ 95°F | Extreme heat — stay hydrated |
| R-4 | Temperature ≤ 45°F | Cold — wear a jacket |
| R-5 | WMO code 95–99 | Thunderstorms — avoid outdoor locations |
| R-6 | No conditions met | Weather looks good — no prep needed |

Rules R-1 and R-2 are cumulative — both fire when precipitation ≥ 80%.

---

## 🧠 Vibe Report

*This section documents the AI/Human collaboration process — where I steered,
where the AI drifted, and what I learned as the architect.*

---

### 1. Where Did the AI's "Vibe" Drift?

The most consistent drift I noticed was the AI's tendency to **collapse
responsibilities into fewer files**. Every time I prompted it to build a new
module, it would start pulling logic from other modules into the same file
"for convenience." For example, when building `advisor.py`, the AI's first
instinct was to import `requests` directly and fetch the weather itself inside
the advice function — completely violating the separation of concerns defined
in the PRD. It had lost the architectural boundary between data fetching and
advice generation.

The second drift was with `main.py`. The AI kept sneaking conditional logic
into it — things like `if precipitation > 50: print("bring umbrella")` —
instead of delegating that responsibility to `advisor.py` where it belonged.
The rules file explicitly prohibited this, but the AI optimized for a "working
app fast" rather than a "clean architecture always."

---

### 2. When Did I Use the "Builder Hammer"?

I had to manually intervene in two specific places:

**Datetime timezone handling** — The AI used `datetime.now()` without
accounting for timezone context, which caused the event filtering logic to
behave inconsistently. Events that were clearly today were being excluded
because the naive datetime comparison was failing at midnight boundaries.
I manually corrected the comparison in `calendar_reader.py` to use
`date.today()` consistently and tested it explicitly.

**Constants not shared between modules** — The AI defined threshold constants
like `RAIN_THRESHOLD_MODERATE = 50` separately in both `weather.py` and
`advisor.py`, creating two sources of truth. If I changed one, the other
would silently fall out of sync. I manually restructured it so that
`advisor.py` imports its constants directly from `weather.py`, keeping
a single source of truth as the PRD intended.

---

### 3. My Most Successful Steering Prompt

The prompt that produced the cleanest, most PRD-aligned output was:

> *"Read `specs/PRD.md` Section 7 (Advice Logic) and `docs/rules.md`
> Section 4 (File-by-File Responsibilities). Build `src/advisor.py`.
> Each rule R-1 through R-6 must be its own private function named
> `_check_[condition]()`. The main entry point is `generate_advice()`.
> Zero print statements anywhere in this file. Return lists of strings,
> never print them. The constants RAIN_THRESHOLD_MODERATE,
> RAIN_THRESHOLD_HEAVY, TEMP_THRESHOLD_HOT, TEMP_THRESHOLD_COLD,
> and THUNDERSTORM_CODES must be imported from weather.py — do not
> redefine them here."*

What made this prompt work was **specificity at the function level** —
I did not just say "build the advisor," I told it exactly how many
functions to create, what to name them, what to import, and what was
explicitly forbidden. Vague prompts produced vague code. Precise prompts
that referenced specific PRD sections produced precise code.

---

### 4. Key Lessons on Context Management

The biggest lesson from this project was that **AI context degrades across
a long session**. Early prompts that referenced the PRD produced clean,
modular output. But as the session grew longer, the AI started forgetting
earlier constraints — reintroducing print statements into modules that had
none, and drifting toward a monolithic style.

My solution was to **re-anchor every prompt** to the PRD and rules.md,
even when it felt repetitive. Treating each prompt as if the AI had never
seen the project before — pasting the relevant PRD section each time —
consistently produced better results than assuming the AI remembered
previous instructions.

The architect's job is not just to write the first prompt. It is to
**manage the AI's context** across every single interaction.

---

## ✅ Success Criteria Checklist

- [x] `python src/main.py` runs without errors
- [x] Weather data is fetched live from Open-Meteo for today's date
- [x] Only today's events are returned from `calendar.json`
- [x] At least one piece of advice is generated per event
- [x] All 41 tests in `tests/` pass via `pytest`
- [x] Rule R-1 is covered by a test with precipitation ≥ 50%
- [x] Rule R-6 (clear weather) is covered by a test with precipitation < 20%
- [x] `advisor.py` contains zero `print()` calls
- [x] `main.py` contains zero business logic

---

