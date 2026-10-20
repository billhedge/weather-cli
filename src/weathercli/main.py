import collections.abc as abc
import sys

import requests_cache

import weathercli.arguments as arguments
import weathercli.exceptions as ex
import weathercli.network as network
from weathercli.data import Current_Weather, Forecast, Location, Units

GEOCODE_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_ENDPOINT = "https://api.open-meteo.com/v1/forecast"


def get_location(api: network.ApiClient, location_name: str) -> Location:
    geocode_response = api.get_json(GEOCODE_ENDPOINT, params={"name": location_name})
    if "results" not in geocode_response or not geocode_response["results"]:
        raise ex.LocationNotFoundError("Location not found. Please check the input and try again.")
    if isinstance(geocode_response["results"][0], dict):
        loc_dict = geocode_response["results"][0]
    else:
        raise ex.InvalidJSONShapeError("Unexpected location data format from the API.")

    try:
        loc = Location(
            name=loc_dict["name"],
            latitude=loc_dict["latitude"],
            longitude=loc_dict["longitude"],
            timezone=loc_dict.get("timezone", "auto"),
        )
        return loc
    except KeyError as e:
        raise ex.InvalidJSONShapeError(f"One or more expected data points was missing: {e}") from e


def get_weather_data(
    api: network.ApiClient, loc: Location, unit_type: str
) -> tuple[Units, Current_Weather, Forecast]:
    forecast_params: dict[str, str | float] = {
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "daily": (
            "temperature_2m_max,temperature_2m_min,apparent_temperature_max,"
            "apparent_temperature_min"
        ),  # plan to add wind speed/dir and precipitation in the future, but for now,
        # just temperature
        "current": "temperature_2m",
        "timezone": loc.timezone,
    }
    if unit_type == "imperial":  # metric units are default, so they don't need to be specified
        forecast_params["wind_speed_unit"] = "mph"
        forecast_params["temperature_unit"] = "fahrenheit"
        forecast_params["precipitation_unit"] = "inch"

    forecast_response = api.get_json(FORECAST_ENDPOINT, params=forecast_params)

    try:
        units_dict = forecast_response["current_units"]
        units = Units(
            temperature_unit=units_dict["temperature_2m"],
            # for future use, if you want to display wind speed and precipitation units
            # wind_speed_unit=units_dict["wind_speed_10m"],
            # precipitation_unit=units_dict["precipitation"],
        )

        current_weather_dict = forecast_response["current"]
        current_weather = Current_Weather(
            date=current_weather_dict["time"],
            temperature=current_weather_dict["temperature_2m"],
        )

        forecast_dict = forecast_response["daily"]
        forecast = Forecast(
            date=forecast_dict["time"][0],
            daily_max_temp=forecast_dict["temperature_2m_max"][0],
            daily_min_temp=forecast_dict["temperature_2m_min"][0],
            apparent_max_temp=forecast_dict["apparent_temperature_max"][0],
            apparent_min_temp=forecast_dict["apparent_temperature_min"][0],
        )

        return units, current_weather, forecast

    except (KeyError, IndexError) as e:
        raise ex.InvalidJSONShapeError(
            f"Unexpected JSON structure received from the API: {e}"
        ) from e


def main(argv: abc.Sequence[str] | None = None) -> int:
    args = arguments.parse_args(argv)

    if not args.no_cache:
        requests_cache.install_cache("weathercli_cache", expire_after=args.cache_expire)

    location_name = " ".join(args.location)
    api = network.ApiClient()
    try:
        loc = get_location(api, location_name)
        units, current_weather, forecast = get_weather_data(api, loc, args.units)
    except ex.AppError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print("Weather in ", location_name, "; Today's date:", current_weather.date)
    print("Current temperature:", current_weather.temperature, units.temperature_unit)
    print("Forecast for:", forecast.date)
    print("Daily maximum temperature:", forecast.daily_max_temp, units.temperature_unit)
    print("Daily minimum temperature:", forecast.daily_min_temp, units.temperature_unit)
    print("Apparent maximum temperature:", forecast.apparent_max_temp, units.temperature_unit)
    print("Apparent minimum temperature:", forecast.apparent_min_temp, units.temperature_unit)

    return 0


if __name__ == "__main__":
    sys.exit(main())
