import json
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, data, status_code=200) -> None:
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data


class FakeSession:
    def __init__(self, geocode, forecast, status_code=200) -> None:
        self.files = {"geocoding": geocode, "forecast": forecast}
        self.status_code = status_code

    def get(self, url, params=None, timeout=None):
        key = "geocoding" if "geocoding" in url else "forecast"
        data = json.loads((FIXTURES / self.files[key]).read_text(encoding="utf-8"))
        return FakeResponse(data, self.status_code)
