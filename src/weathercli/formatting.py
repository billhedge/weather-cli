import weathercli.data as d

GAP = "  "
COLUMNS = (("Date", 10), ("High", 7), ("Feels hi", 11), ("Low", 7), ("Feels lo", 11))


def formatted_output(
    location_name: str,
    units: d.Units,
    current_weather: d.CurrentWeather,
    forecasts: list[d.DailyForecast],
) -> str:
    adj_columns = (COLUMNS[0],) + tuple(
        (f"{title} {units.temperature_unit}", max(len(f"{title} {units.temperature_unit}"), width))
        for title, width in COLUMNS[1:]
    )
    (date_title, date_width), *rest = adj_columns
    rows = []

    rows.append(
        f"Weather in {location_name} at {current_weather.observed_at.strftime('%Y-%m-%d %H:%M')}"
    )

    rows.append(f"Now: {current_weather.temp:.1f} {units.temperature_unit}")
    rows.append("")

    header = GAP.join([f"{date_title:<{date_width}}"] + [f"{title:>{w}}" for title, w in rest])

    rule = GAP.join(["-" * w for _, w in adj_columns])

    rows.append(header)
    rows.append(rule)

    for day in forecasts:
        date_str = f"{day.forecast_date.strftime('%a %b %d'):<{date_width}}"

        temps = (
            day.daily_max_temp,
            day.apparent_max_temp,
            day.daily_min_temp,
            day.apparent_min_temp,
        )

        formatted_temps = GAP.join(
            [f"{temp:>{temp_width}.1f}" for temp, (_, temp_width) in zip(temps, rest, strict=True)]
        )

        rows.append(GAP.join([date_str, formatted_temps]))

    return "\n".join(rows)
