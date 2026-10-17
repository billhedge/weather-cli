# Project 1 spec: weather + air quality CLI

You write the code. This document gives you the target, the API facts, and a milestone order. It has hints, not solutions. Each milestone is meant to be one branch and one pull request.

## Target behavior

```console
$ weather "Springfield, Illinois" --units metric --days 3
<location line>
<current conditions: temperature, feels-like, description, humidity, wind>
<air quality line, if available>

<N-day forecast table: date, high, low, precipitation, description>
```

Exit code 0 on success, 1 on a lookup or network error (one-line message on stderr, no traceback), 2 on a usage error.

## The APIs (free, no key)

Confirm every parameter against the official docs at https://open-meteo.com before relying on it. I have not been able to call these live from my side.

1. **Geocoding**: `GET https://geocoding-api.open-meteo.com/v1/search` with `name`, `count`, `language`, `format`. Each result has `name`, `latitude`, `longitude`, `country`, `country_code`, `admin1` (state or region), `timezone`. Empty fields can be omitted, and a search with no matches may have no `results` key at all.
2. **Forecast**: `GET https://api.open-meteo.com/v1/forecast` with `latitude`, `longitude`, `current=...`, `daily=...`, `timezone=auto`, `forecast_days`, plus unit options `temperature_unit`, `wind_speed_unit`, `precipitation_unit`. Look up the variable names you need: temperature, apparent temperature, relative humidity, wind speed, weather code (current); max/min temperature, precipitation sum, weather code (daily).
3. **Air quality**: `GET https://air-quality-api.open-meteo.com/v1/air-quality` with `latitude`, `longitude`, `current=us_aqi,pm2_5,pm10`. Values can be null.
4. **Weather codes**: the forecast returns numeric WMO codes. You will need your own code-to-text table. Open-Meteo's docs list the codes.

## Milestones

### 1. Hello, Open-Meteo (a single script, no structure yet)
Geocode a hard-coded city and print its latitude and longitude.
- `requests.get(..., params=..., timeout=...)`. Always pass a timeout, and find out what happens without one.
- `response.raise_for_status()` and `response.json()`.
- Print the raw JSON once and read it before writing any parsing code.

Done when: you can explain what each field in the result means.

### 2. Models and forecast parsing
Move into `src/weathercli/`. Fetch the forecast and turn the response into your own types instead of passing raw dicts around.
- `dataclasses` (try `frozen=True`) for location, current conditions, and one forecast day.
- Parse defensively: what should happen if a key is missing or an array is shorter than expected?
- Convention check: where does `float(x)` belong, and where should a bad value turn into an error?

Done when: a function takes a location and returns typed objects, and no dict access leaks past it.

### 3. Errors and retries
Network code fails in boring ways. Handle them on purpose.
- Define a small exception hierarchy (one base class the CLI can catch).
- Cover: timeout, connection error, HTTP error status, invalid JSON, JSON of the wrong shape, city not found.
- Read about `requests.adapters.HTTPAdapter` plus `urllib3.util.retry.Retry` for automatic retries with backoff.
- Gotcha worth discovering yourself: what is `bool(response)` for a 404? Check the requests docs on `Response.__bool__`.

Done when: every failure produces a distinct, readable message and none shows a traceback.

### 4. The CLI
- `argparse`: city (several words, no quotes needed), `--units`, `--days`, `--json`.
- Write a `main(argv=None) -> int` that returns the exit code instead of calling `sys.exit` itself. Think about why this makes tests easier.
- Separate formatting (data in, string out) from printing.
- Python idioms to practice: f-string format specs for aligned columns, `datetime.date.fromisoformat`, `dataclasses.asdict` for `--json`.

Done when: all the example commands in your README work.

### 5. Caching
Be polite to a free API: don't ask for the same thing twice in a row.
- Cache on disk (JSON files) with a time-to-live. Decide on a cache key and what to do about corrupt files.
- Think about testability: how would you test expiry without calling `time.sleep`?
- Different data goes stale at different speeds. A city's coordinates versus today's forecast.
- Use `pathlib`, and pick a sensible default cache directory.

Done when: running the same command twice makes one network call, and `--no-cache` / `--clear-cache` work.

### 6. Air quality, gracefully
Add the air quality endpoint.
- Design question: if this call fails but the forecast succeeded, should the whole command fail? Decide, and write down why in the README's design notes.
- Handle null values per field.
- Map AQI numbers to categories (the US AQI scale is on the EPA site).

Done when: pulling the network plug on only this endpoint still gets the user a forecast.

### 7. Tests
Aim for tests that never touch the real network.
- `pytest` fixtures, `tmp_path`, `monkeypatch`, `capsys`, and `pytest.mark.parametrize`.
- Dependency injection is the key idea: let the client accept a session object, so a tiny fake class can stand in for `requests.Session`.
- Test the failure paths at least as carefully as the happy path.
- Run `pytest --cov=weathercli --cov-report=term-missing` and look at what you missed.

Done when: CI is green on Python 3.10 to 3.13.

### 8. Polish
- Register the `weather` console script in `pyproject.toml` (the TODO is already there).
- Fill in the README: features, usage with real output, design notes, roadmap.
- `ruff check`, `ruff format`, and `mypy` all clean.
- Add `__main__.py` so `python -m weathercli` works.

## Stretch goals
- Compare two cities side by side.
- A 7-day temperature chart with matplotlib (`--chart`).
- Favorite cities in a config file.

## When you want a review
Push your branch, then paste the code or the PR link here. Tell me which milestone it is and what you're unsure about, and I'll review it like a pull request: bugs, Python idioms, structure, tests.
