import functools

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


def test_main_installs_cache(use_fake_session, monkeypatch):
    use_fake_session("geocode_tokyo.json", "forecast_tokyo_1day_imperial.json")
    calls = []
    monkeypatch.setattr(
        main.requests_cache,
        "install_cache",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    code = main.main(["Tokyo", "--cache-expire", "7200"])

    assert code == 0
    assert calls == [(("weathercli_cache",), {"expire_after": 7200})]
    # one call; check the cache name and expire_after=7200
