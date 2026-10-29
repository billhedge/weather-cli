import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True)
class CurrentWeather:
    observed_at: datetime.datetime
    temp: float


@dataclass(frozen=True)
class DailyForecast:
    forecast_date: datetime.date
    daily_max_temp: float
    daily_min_temp: float
    apparent_max_temp: float
    apparent_min_temp: float


@dataclass(frozen=True)
class Units:
    temperature_unit: str
    # for future use, if you want to display wind speed and precipitation units
    # wind_speed_unit: str
    # precipitation_unit: str
