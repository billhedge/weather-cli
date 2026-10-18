from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import weathercli.exceptions as ex


class ApiClient:
    def __init__(self, session: requests.Session | None = None, timeout: float = 10):
        self.session = session if session is not None else self.build_session()
        self.timeout = timeout

    @staticmethod
    def build_session() -> requests.Session:
        """Builds a requests session with retry logic."""
        session = requests.Session()
        status_force_list = [429, 500, 502, 503, 504]
        backoff_factor = 0.5
        retry_strategy = Retry(
            total=3,
            status_forcelist=status_force_list,
            backoff_factor=backoff_factor,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def get(self, url: str, params: dict[str, str | float]) -> requests.Response:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.exceptions.Timeout as e:
            raise ex.NetworkTimeoutError("Network request timed out.") from e
        except requests.exceptions.ConnectionError as e:
            raise ex.NetworkConnectionError("Network connection error occurred.") from e
        except requests.exceptions.RequestException as e:
            raise ex.UnexpectedResponseError("An unexpected error occurred.") from e
        if 500 <= response.status_code < 600:
            raise ex.NetworkHTTP5xxError(f"Server error occurred: {response.status_code}")
        if response.status_code == 429:
            raise ex.RateLimitError("API rate limit exceeded. Please try again later.")
        if 400 <= response.status_code < 500:
            raise ex.HTTPClientError(f"Client error occurred: {response.status_code}")
        if 200 <= response.status_code < 300:
            return response
        raise ex.UnexpectedResponseError(f"Unexpected HTTP error occurred: {response.status_code}")

    def get_json(self, url: str, params: dict[str, str | float]) -> dict[str, Any]:
        """Helper method to get JSON data from a URL with error handling."""
        response = self.get(url, params=params)
        try:
            data = response.json()
        except ValueError as e:
            raise ex.InvalidJSONError("Invalid JSON response received.") from e
        if not isinstance(data, dict):
            raise ex.InvalidJSONShapeError("Unexpected JSON structure received from the API.")
        return data
