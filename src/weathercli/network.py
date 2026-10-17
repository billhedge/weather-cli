import requests


class ApiClient:
    def __init__(self, session: requests.Session | None = None, timeout: float = 10):
        self.session = session if session is not None else requests.Session()
        self.timeout = timeout

    def get(self, url: str, params: dict[str, str | float]) -> requests.Response:
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response
