import argparse
import collections.abc as abc


def parse_args(argv: abc.Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("location", type=str, help="Location name for weather forecast", nargs="+")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching of API responses")
    parser.add_argument(
        "--cache-expire",
        type=int,
        default=3600,
        help="Cache expiration time in seconds (default: 3600)",
    )
    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="imperial",
        help="Unit type for wind speed, temperature, and precipitation (default: imperial)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days for the forecast (default: 1, max: 16)",
        choices=range(1, 17),
        metavar="N",
    )
    parser.add_argument("--json", action="store_true", help="Output the forecast in JSON format")

    return parser.parse_args(argv)
