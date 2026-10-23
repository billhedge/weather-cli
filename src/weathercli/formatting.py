import weathercli.data as d


def formatted_output(
    location_name: str,
    units: d.Units,
    current_weather: d.CurrentWeather,
    forecasts: list[d.DailyForecast],
) -> str:
    txt_format = "<12"
    num_format = ">7.1f"
    output = f"Weather in {location_name} at {current_weather.observed_at}\n"
    output += f"{'Item':{txt_format}}|Temp ({units.temperature_unit.strip()})\n"
    output += f"{'-':{txt_format}}|{'-' * 10}\n"

    for day in forecasts:
        output += f"{'Daily maximum temperature':{txt_format}}|{day.daily_max_temp:{num_format}}\n"
        output += f"{'Daily minimum temperature':{txt_format}}|{day.daily_min_temp:{num_format}}\n"
        output += (
            f"{'Apparent maximum temperature':{txt_format}}|{day.apparent_max_temp:{num_format}}\n"
        )
        output += (
            f"{'Apparent minimum temperature':{txt_format}}|{day.apparent_min_temp:{num_format}}\n"
        )

    return output
