import functools
import json

import pytest

from fakes import FakeSession
from weathercli import main, network


@pytest.fixture
def use_fake_session(monkeypatch):
    """Make main() build its ApiClient around a FakeSession."""

    def _use(geocode, forecast):
        monkeypatch.setattr(
            network,
            "ApiClient",
            functools.partial(
                network.ApiClient,
                session=FakeSession(geocode, forecast),  # type: ignore[arg-type]
            ),
        )

    return _use


def test_main_success(use_fake_session, capsys):
    use_fake_session("geocode_tokyo.json", "forecast_tokyo_1day_imperial.json")

    code = main.main(["Tokyo", "--no-cache"])

    captured = capsys.readouterr()
    assert code == 0
    assert "Weather in Tokyo" in captured.out
    assert captured.err == ""


def test_main_unknown_location(use_fake_session, capsys):
    use_fake_session("geocode_nonsense.json", "forecast_tokyo_1day_imperial.json")

    code = main.main(["Zzzzzz", "--no-cache"])

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "Location not" in captured.err


@pytest.mark.parametrize(
    ("extra_args", "expected"),
    [([], 3600), (["--cache-expire", "7200"], 7200), (["--no-cache"], None)],
    ids=["default", "custom", "no-cache"],
)
def test_main_passes_cache_setting(monkeypatch, extra_args, expected):
    real_client = network.ApiClient  # capture BEFORE patching
    calls = []

    def spy(**kwargs):
        calls.append(kwargs)
        return real_client(
            session=FakeSession("geocode_tokyo.json", "forecast_tokyo_1day_imperial.json")  # type: ignore[arg-type]
        )

    monkeypatch.setattr(network, "ApiClient", spy)

    code = main.main(["Tokyo", *extra_args])

    assert calls == [{"cache_expire": expected}]
    assert code == 0


def test_main_success_json(use_fake_session, capsys):
    use_fake_session("geocode_tokyo.json", "forecast_tokyo_1day_imperial.json")

    code = main.main(["Tokyo", "--no-cache", "--json"])

    captured = capsys.readouterr()
    assert code == 0
    data = json.loads(captured.out)
    assert data["location_name"] == "Tokyo"
    assert len(data["weather"]["forecasts"]) == 1
    assert captured.err == ""


def test_main_unknown_location_json(use_fake_session, capsys):
    use_fake_session("geocode_nonsense.json", "forecast_tokyo_1day_imperial.json")

    code = main.main(["Zzzzzz", "--no-cache", "--json"])

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "Location not" in captured.err
