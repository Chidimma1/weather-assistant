import sys

from advisor import generate_advice
from calendar_reader import load_events
from weather import fetch_weather


def main() -> None:
    """Run the weather-aware advisor CLI."""
    try:
        weather = fetch_weather()
        events = load_events()
        advice_results = generate_advice(weather, events)
    except ConnectionError:
        print("Unable to fetch weather data. Please check your network connection and try again.")
        sys.exit(1)
    except FileNotFoundError as exc:
        print(str(exc))
        sys.exit(1)

    for result in advice_results:
        event = result["event"]
        advice_lines = result["advice"]

        print(f"Title: {event.title}")
        print(f"Start: {event.start.strftime('%Y-%m-%d %H:%M')}")
        print(f"End:   {event.end.strftime('%Y-%m-%d %H:%M')}")
        print(f"Location: {event.location}")
        print("Advice:")
        for line in advice_lines:
            print(f"  - {line}")
        print()


if __name__ == "__main__":
    main()
