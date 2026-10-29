import datetime

import pytest

import weathercli.exceptions as ex
import weathercli.main as main
import weathercli.network as network
from fakes import FakeSession


def test_tokyo_happy_path():
    api = network.ApiClient(
        session=FakeSession("geocode_tokyo.json", "forecast_tokyo_5day_imperial.json")  # type: ignore[arg-type]
    )
    loc = main.get_location(api, "Tokyo")
    units, current, forecasts = main.get_weather_data(api, loc, "imperial", 5)

    assert loc.name == "Tokyo"
    assert forecasts[0].forecast_date == datetime.date(2026, 10, 22)
    assert forecasts[0].daily_max_temp == 71.5
    assert current.temp == 68.6
    assert len(forecasts) == 5
    assert units.temperature_unit == "°F"


def test_new_york_happy_path():
    api = network.ApiClient(
        session=FakeSession("geocode_new_york.json", "forecast_new_york_3day_metric.json")  # type: ignore[arg-type]
    )
    loc = main.get_location(api, "New York")
    units, current, forecasts = main.get_weather_data(api, loc, "metric", 3)

    assert loc.name == "New York"
    assert forecasts[0].forecast_date == datetime.date(2026, 10, 21)
    assert forecasts[0].daily_max_temp == 17.5
    assert current.temp == 10.5
    assert len(forecasts) == 3
    assert units.temperature_unit == "°C"


def test_unknown_location():
    api = network.ApiClient(
        session=FakeSession("geocode_nonsense.json", "forecast_tokyo_5day_imperial.json")  # type: ignore[arg-type]
    )
    with pytest.raises(ex.LocationNotFoundError):
        main.get_location(api, "Tokyo")


@pytest.mark.parametrize(
    "status, expected",
    [(404, ex.HTTPClientError), (429, ex.RateLimitError), (503, ex.NetworkHTTP5xxError)],
)
def test_http_errors(status, expected):
    api = network.ApiClient(
        session=FakeSession(  # type: ignore[arg-type]
            "geocode_tokyo.json",
            "forecast_tokyo_5day_imperial.json",
            status_code=status,
        )
    )
    with pytest.raises(expected):
        main.get_location(api, "Tokyo")


@pytest.mark.parametrize(
    "geocode", ["geocode_new_york_missing_latitude.json", "geocode_tokyo_bad_result.json"]
)
def test_broken_fixture(geocode):
    api = network.ApiClient(
        session=FakeSession(  # type: ignore[arg-type]
            geocode,
            "forecast_tokyo_5day_imperial.json",
        )
    )
    with pytest.raises(ex.InvalidJSONShapeError):
        main.get_location(api, "New York")
