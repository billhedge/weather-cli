import datetime

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

units_f = Units(temperature_unit="°F")
units_c = Units(temperature_unit="°C")
units_a = Units(temperature_unit="°Axolotl")


def test_formatting_f():
    output = weathercli.formatting.formatted_output(loc_str, units_f, cw, [df1, df2])
    correct = []
    correct.append("Weather in New York at 2026-10-22 11:00")
    correct.append("Now: 72.1 °F")
    correct.append("")
    correct.append("Date        High °F  Feels hi °F   Low °F  Feels lo °F")
    correct.append("----------  -------  -----------  -------  -----------")
    correct.append("Thu Oct 22     73.1         75.5     60.2         62.5")
    correct.append("Fri Oct 23     72.0         72.3     63.5         65.1")

    assert output == "\n".join(correct)


def test_formatting_c():
    output = weathercli.formatting.formatted_output(loc_str, units_c, cw, [df1, df2])
    correct = []
    correct.append("Weather in New York at 2026-10-22 11:00")
    correct.append("Now: 72.1 °C")
    correct.append("")
    correct.append("Date        High °C  Feels hi °C   Low °C  Feels lo °C")
    correct.append("----------  -------  -----------  -------  -----------")
    correct.append("Thu Oct 22     73.1         75.5     60.2         62.5")
    correct.append("Fri Oct 23     72.0         72.3     63.5         65.1")

    assert output == "\n".join(correct)


def test_formatting_axolotl():
    output = weathercli.formatting.formatted_output(loc_str, units_a, cw, [df1, df2])
    correct = []
    correct.append("Weather in New York at 2026-10-22 11:00")
    correct.append("Now: 72.1 °Axolotl")
    correct.append("")
    correct.append("Date        High °Axolotl  Feels hi °Axolotl  Low °Axolotl  Feels lo °Axolotl")
    correct.append("----------  -------------  -----------------  ------------  -----------------")
    correct.append("Thu Oct 22           73.1               75.5          60.2               62.5")
    correct.append("Fri Oct 23           72.0               72.3          63.5               65.1")

    assert output == "\n".join(correct)
