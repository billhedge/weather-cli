import sys

import requests
import requests_cache

from weathercli.data import Current_Weather, Forecast, Location, Units

GEOCODE_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_ENDPOINT = "https://api.open-meteo.com/v1/forecast"

requests_cache.install_cache("weathercli_cache", expire_after=3600)


def get_location() -> Location:
    geocode_response = requests.get(
        GEOCODE_ENDPOINT, params={"name": input("Enter a location: ")}, timeout=10
    )
    geocode_response.raise_for_status()

    try:
        loc_dict = geocode_response.json()["results"][0]
        loc = Location(
            name=loc_dict["name"],
            latitude=loc_dict["latitude"],
            longitude=loc_dict["longitude"],
            timezone=loc_dict["timezone"],
        )
        return loc
    except (KeyError, IndexError):
        print(
            "Error: Unable to retrieve location data. Please check the location name and try again."
        )
        sys.exit(1)


def get_weather_data(loc: Location) -> tuple[Units, Current_Weather, Forecast]:
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
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
    }
    forecast_response = requests.get(FORECAST_ENDPOINT, params=forecast_params, timeout=10)
    forecast_response.raise_for_status()

    try:
        response_data = forecast_response.json()

        units_dict = response_data["current_units"]
        units = Units(
            temperature_unit=units_dict["temperature_2m"],
            # for future use, if you want to display wind speed and precipitation units
            # wind_speed_unit=units_dict["wind_speed_10m"],
            # precipitation_unit=units_dict["precipitation"],
        )

        current_weather_dict = response_data["current"]
        current_weather = Current_Weather(
            date=current_weather_dict["time"],
            temperature=current_weather_dict["temperature_2m"],
        )

        forecast_dict = response_data["daily"]
        forecast = Forecast(
            date=forecast_dict["time"][0],
            daily_max_temp=forecast_dict["temperature_2m_max"][0],
            daily_min_temp=forecast_dict["temperature_2m_min"][0],
            apparent_max_temp=forecast_dict["apparent_temperature_max"][0],
            apparent_min_temp=forecast_dict["apparent_temperature_min"][0],
        )

        return units, current_weather, forecast

    except (KeyError, IndexError):
        print("Error: Unable to retrieve weather data. Please try again later.")
        sys.exit(1)


def main() -> None:
    loc = get_location()
    units, current_weather, forecast = get_weather_data(loc)

    print("Today's date:", current_weather.date)
    print("Current temperature:", current_weather.temperature, units.temperature_unit)
    print("Forecast for:", forecast.date)
    print("Daily maximum temperature:", forecast.daily_max_temp, units.temperature_unit)
    print("Daily minimum temperature:", forecast.daily_min_temp, units.temperature_unit)
    print("Apparent maximum temperature:", forecast.apparent_max_temp, units.temperature_unit)
    print("Apparent minimum temperature:", forecast.apparent_min_temp, units.temperature_unit)


if __name__ == "__main__":
    main()
