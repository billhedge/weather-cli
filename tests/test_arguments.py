import pytest

from weathercli import arguments


def test_defaults():
    args = arguments.parse_args(["Tokyo"])

    assert args.location == ["Tokyo"]
    assert args.units == "imperial"
    assert args.days == 1
    assert args.cache_expire == 3600
    assert args.no_cache is False
    assert args.json is False


def test_multiword_location():
    args = arguments.parse_args(["New", "York"])

    assert args.location == ["New", "York"]


def test_all_options():
    args = arguments.parse_args(
        [
            "Tokyo",
            "--units",
            "metric",
            "--days",
            "5",
            "--cache-expire",
            "60",
            "--no-cache",
            "--json",
        ]
    )

    assert args.units == "metric"
    assert args.days == 5  # int, not "5"
    assert args.cache_expire == 60
    assert args.no_cache is True
    assert args.json is True


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["Tokyo", "--days", "0"],
        ["Tokyo", "--days", "17"],
        ["Tokyo", "--days", "three"],
        ["Tokyo", "--units", "kelvin"],
        ["Tokyo", "--cache-expire", "soon"],
        ["Tokyo", "--bogus"],
    ],
    ids=[
        "no-location",
        "days-0",
        "days-17",
        "days-text",
        "units-kelvin",
        "expire-text",
        "unknown-flag",
    ],
)
def test_usage_errors_exit_2(argv, capsys):
    with pytest.raises(SystemExit) as exc_info:
        arguments.parse_args(argv)

    assert exc_info.value.code == 2
    assert "usage:" in capsys.readouterr().err
