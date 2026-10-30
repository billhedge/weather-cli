# weathercli

A command-line tool that prints a single-day or multi-day (up to 16 days) weather forecast for a location, using the free Open-Meteo API. Output is a table or JSON. Built as a learning project covering Python API clients, error handling, and offline testing.

Table output (the default):

```bash
weather Tokyo --days 3
```
```
Weather in Tokyo at 2026-10-30 22:30
Now: 57.9 °F

Date        High °F  Feels hi °F   Low °F  Feels lo °F
----------  -------  -----------  -------  -----------
Fri Oct 30     68.3         69.0     53.8         52.9
Sat Oct 31     73.2         71.8     53.7         53.8
Sun Nov 01     66.9         64.6     54.3         52.5
```

JSON output:

```bash
weather Tokyo --days 1 --json
```
```json
{
  "location_name": "Tokyo",
  "units": {
    "temp": "\u00b0F"
  },
  "weather": {
    "current": {
      "observed_at": "2026-10-30T23:00:00",
      "temp": 57.8
    },
    "forecasts": [
      {
        "date": "2026-10-30",
        "daily_max_temp": 68.3,
        "apparent_max_temp": 69.0,
        "daily_min_temp": 53.8,
        "apparent_min_temp": 52.9
      }
    ]
  }
}
```

## Features

- Multi-day forecasts, up to 16 days
- Metric or imperial units
- Table or JSON output
- Response caching with retries

## Install

Requires Python 3.10 or newer.

```bash
git clone https://github.com/billhedge/weather-cli.git
cd weather-cli
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -e .
```
On Windows PowerShell, if activation fails with "running scripts is disabled", run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

## Usage

Usage: `weather LOCATION [options]`

```bash
weather Tokyo
weather New York --days 3 --units metric    # Multi-word locations don't need quotes!
weather Tokyo --json
weather Tokyo --no-cache
weather --help
```
Exit codes: `0` success, `1` expected failure (unknown location, network, or API error), `2` invalid arguments. Check the last one with `echo $?` (PowerShell: `echo $LASTEXITCODE`).

Note that `python -m weathercli Tokyo` works, too!

| Option | Default | Description |
|---|---|---|
| `--days N` | `1` | Forecast length, 1 to 16 days |
| `--units {metric,imperial}` | `imperial` | Temperature units |
| `--json` | off | Print JSON instead of a table |
| `--no-cache` | off | Skip the response cache |
| `--cache-expire SECONDS` | `3600` (1 hour) | How long cached responses are kept |

Cached responses are stored in `weathercli_cache.sqlite` in the working directory. To clear the local cache:

```bash
rm -f weathercli_cache.sqlite          # Windows: Remove-Item weathercli_cache.sqlite -ErrorAction SilentlyContinue
```

## Development

Set up the environment as in [Install](#install), but instead of the last step install the development tools too:

```bash
pip install -e ".[dev]"
```

Run the checks before committing:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

Coverage testing:

```bash
pytest --cov=weathercli --cov-report=term-missing
pytest --cov=weathercli --cov-branch --cov-report=term-missing   # include branches
pytest --cov=weathercli --cov-report=html                        # then open htmlcov/index.html
```

CI runs the same checks on Python 3.10 to 3.13.

## Design notes

- **Error handling.** Every expected failure derives from `AppError`. `main()` catches it and prints an error message to `stderr`, without the traceback, and exits with code `1`. Anything that isn't an `AppError` is a bug and is not caught, so the traceback will show. There are three groups:
  - `NetworkError`: the request couldn't be completed (timeouts, connection failures, 5xx, rate limiting). Trying the request again later may work without changing it.
  - `InputError`: something the user supplied, such as a location that doesn't exist. The user should check what they entered and try again.
  - `UnexpectedResponseError`: the API replied, but with something the client can't use, like invalid JSON, a changed structure, or a 4xx status other than 429. This error indicates either a bug or that something may have changed within the API itself.
- **Injectable HTTP client.** `ApiClient` accepts an optional session and builds its own only when none is given, so tests hand it a fake and run without touching the network. The retry policy is attached only to the session `ApiClient` builds itself, so an injected session is never modified.
- **Retries and timeouts.** Failed connections and responses with HTTP statuses 429, 500, 502, 503, and 504 are automatically retried up to three times, with an exponential backoff (`backoff_factor=0.5`) between attempts. All requests have a timeout (default is 10 seconds).
- **Offline tests with real data.** Fixtures are responses captured from the live API; the malformed ones used for failure paths are edited copies. Tests inject a fake session into the real `ApiClient`, so only the HTTP transport is replaced, and the suite runs without a network connection.
- **Caching.** Responses are cached by a `requests-cache` `CachedSession` that `ApiClient` builds when caching is enabled, not by the library's global `install_cache`. The global approach patches `requests` for the whole process, which leaks into tests and into any program that imports the package. With a session, caching is limited to the client that asked for it, and `ApiClient` never adds caching to a session it was given.
- **Output.** Column widths come from the headers, including the unit label, so the table stays aligned whatever the units. JSON output is a list of per-day records with ISO 8601 dates and numeric values. Stdout carries only results and stderr carries errors, so piping works.

## Roadmap

- Current air quality (US AQI, PM2.5, and PM10) from Open-Meteo's air quality API, shown beside the forecast and as a new section in the JSON output.

## Data and attribution

Weather and air quality data by [Open-Meteo.com](https://open-meteo.com).
Check their [terms](https://open-meteo.com/en/terms) for usage limits and attribution requirements.

## License

MIT. See [LICENSE](LICENSE).
