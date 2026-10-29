import datetime
import json

import pytest

import weathercli.formatting
from weathercli.data import CurrentWeather, DailyForecast, Units

loc_str = "New York"
cw = CurrentWeather(observed_at=datetime.datetime(2026, 10, 22, 11, 0), temp=72.1)
df1 = DailyForecast(
    forecast_date=datetime.date(2026, 10, 22),
    daily_max_temp=73.1,
    daily_min_temp=60.2,
    apparent_max_temp=75.5,
    apparent_min_temp=62.5,
)
df2 = DailyForecast(
    forecast_date=datetime.date(2026, 10, 23),
    daily_max_temp=72.0,
    daily_min_temp=63.5,
    apparent_max_temp=72.3,
    apparent_min_temp=65.1,
)
df3 = DailyForecast(
    forecast_date=datetime.date(2026, 10, 24),
    daily_max_temp=105.7,
    daily_min_temp=-43.2,
    apparent_max_temp=121.2,
    apparent_min_temp=-123.1,
)

units_f = Units(temperature_unit="°F")
units_c = Units(temperature_unit="°C")
units_a = Units(temperature_unit="°Axolotl")


def test_formatting_f():
    output = weathercli.formatting.formatted_output(loc_str, units_f, cw, [df1, df2, df3])
    correct = []
    correct.append("Weather in New York at 2026-10-22 11:00")
    correct.append("Now: 72.1 °F")
    correct.append("")
    correct.append("Date        High °F  Feels hi °F   Low °F  Feels lo °F")
    correct.append("----------  -------  -----------  -------  -----------")
    correct.append("Thu Oct 22     73.1         75.5     60.2         62.5")
    correct.append("Fri Oct 23     72.0         72.3     63.5         65.1")
    correct.append("Sat Oct 24    105.7        121.2    -43.2       -123.1")

    assert output == "\n".join(correct)


def test_formatting_c():
    output = weathercli.formatting.formatted_output(loc_str, units_c, cw, [df1, df2, df3])
    correct = []
    correct.append("Weather in New York at 2026-10-22 11:00")
    correct.append("Now: 72.1 °C")
    correct.append("")
    correct.append("Date        High °C  Feels hi °C   Low °C  Feels lo °C")
    correct.append("----------  -------  -----------  -------  -----------")
    correct.append("Thu Oct 22     73.1         75.5     60.2         62.5")
    correct.append("Fri Oct 23     72.0         72.3     63.5         65.1")
    correct.append("Sat Oct 24    105.7        121.2    -43.2       -123.1")

    assert output == "\n".join(correct)


def test_formatting_axolotl():
    output = weathercli.formatting.formatted_output(loc_str, units_a, cw, [df1, df2, df3])
    correct = []
    correct.append("Weather in New York at 2026-10-22 11:00")
    correct.append("Now: 72.1 °Axolotl")
    correct.append("")
    correct.append("Date        High °Axolotl  Feels hi °Axolotl  Low °Axolotl  Feels lo °Axolotl")
    correct.append("----------  -------------  -----------------  ------------  -----------------")
    correct.append("Thu Oct 22           73.1               75.5          60.2               62.5")
    correct.append("Fri Oct 23           72.0               72.3          63.5               65.1")
    correct.append("Sat Oct 24          105.7              121.2         -43.2             -123.1")

    assert output == "\n".join(correct)


def test_formatting_empty():
    output = weathercli.formatting.formatted_output(loc_str, units_f, cw, [])
    correct = []
    correct.append("Weather in New York at 2026-10-22 11:00")
    correct.append("Now: 72.1 °F")
    correct.append("")
    correct.append("Date        High °F  Feels hi °F   Low °F  Feels lo °F")
    correct.append("----------  -------  -----------  -------  -----------")

    assert output == "\n".join(correct)


@pytest.mark.parametrize("units", [units_f, units_c, units_a], ids=["F", "C", "axolotl"])
def test_table_alignment(units):
    output = weathercli.formatting.formatted_output(loc_str, units, cw, [df1, df2, df3])
    table = output.splitlines()[3:]

    assert len({len(line) for line in table}) == 1
    assert table[0].startswith("Date")


@pytest.mark.parametrize("units", [units_f, units_c, units_a], ids=["F", "C", "axolotl"])
def test_json(units):
    output = weathercli.formatting.json_output(loc_str, units, cw, [df1, df2, df3])
    correct = {
        "location_name": "New York",
        "units": {"temp": units.temperature_unit},
        "weather": {
            "current": {"observed_at": "2026-10-22T11:00:00", "temp": 72.1},
            "forecasts": [
                {
                    "date": "2026-10-22",
                    "daily_max_temp": 73.1,
                    "apparent_max_temp": 75.5,
                    "daily_min_temp": 60.2,
                    "apparent_min_temp": 62.5,
                },
                {
                    "date": "2026-10-23",
                    "daily_max_temp": 72.0,
                    "apparent_max_temp": 72.3,
                    "daily_min_temp": 63.5,
                    "apparent_min_temp": 65.1,
                },
                {
                    "date": "2026-10-24",
                    "daily_max_temp": 105.7,
                    "apparent_max_temp": 121.2,
                    "daily_min_temp": -43.2,
                    "apparent_min_temp": -123.1,
                },
            ],
        },
    }

    assert json.loads(output) == correct


def test_json_empty_forecasts():
    output = weathercli.formatting.json_output(loc_str, units_f, cw, [])
    correct = {
        "location_name": "New York",
        "units": {"temp": units_f.temperature_unit},
        "weather": {
            "current": {"observed_at": "2026-10-22T11:00:00", "temp": 72.1},
            "forecasts": [],
        },
    }

    assert json.loads(output) == correct
