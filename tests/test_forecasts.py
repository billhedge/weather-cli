import pytest

import weathercli.exceptions as ex
import weathercli.main as main
import weathercli.network as network
from fakes import FakeSession

bad_date = "forecast_tokyo_5day_imperial_bad_date.json"
missing_daily = "forecast_tokyo_5day_imperial_missing_daily.json"
trunc_array = "forecast_tokyo_5day_imperial_trunc_array.json"


@pytest.mark.parametrize(
    "forecast_file, cause",
    [(bad_date, ValueError), (missing_daily, KeyError), (trunc_array, ValueError)],
)
def test_malformed_forecast_raises_shape_error(forecast_file, cause):
    api = network.ApiClient(
        session=FakeSession(  # type: ignore[arg-type]
            "geocode_tokyo.json",
            forecast_file,
        )
    )

    loc = main.get_location(api, "Tokyo")
    with pytest.raises(ex.InvalidJSONShapeError) as exc_info:
        main.get_weather_data(api, loc, "imperial", 5)
    assert isinstance(exc_info.value.__cause__, cause)
