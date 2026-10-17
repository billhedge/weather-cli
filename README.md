# weathercli

TODO: one or two sentences. What does it do, and for whom?

<!-- TODO: paste a real terminal run here, or add a screenshot/GIF -->

## Features

- TODO

## Install

Requires Python 3.10+.

```console
git clone https://github.com/<your-username>/weather-cli.git
cd weather-cli
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

TODO: show the commands and options once the CLI exists.

## Development

```console
pytest
ruff check . && ruff format --check .
mypy
```

## Design notes

TODO: a few sentences on the decisions you made (structure, error handling,
caching, how you test without the network) and why.

## Data and attribution

Weather and air quality data by [Open-Meteo.com](https://open-meteo.com).
Check their [terms](https://open-meteo.com/en/terms) for usage limits and attribution requirements.

## License

MIT. See [LICENSE](LICENSE).
