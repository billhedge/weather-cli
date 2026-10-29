import pytest
import requests

from fakes import BadJsonResponse, FakeResponse, RaisingSession, StaticSession
from weathercli import exceptions as ex
from weathercli import network


def make_client(session, **kwargs):
    return network.ApiClient(session=session, **kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("raised", "expected"),
    [
        (requests.exceptions.Timeout, ex.NetworkTimeoutError),
        (requests.exceptions.ReadTimeout, ex.NetworkTimeoutError),
        (requests.exceptions.ConnectionError, ex.NetworkConnectionError),
        (requests.exceptions.SSLError, ex.NetworkConnectionError),
        (requests.exceptions.ConnectTimeout, ex.NetworkTimeoutError),  # the catch-order check
        (requests.exceptions.TooManyRedirects, ex.UnexpectedResponseError),
    ],
    ids=["timeout", "read-timeout", "connection", "ssl", "connect-timeout", "redirects"],
)
def test_transport_errors_are_translated(raised, expected):
    original = raised("boom")
    client = make_client(RaisingSession(original))

    with pytest.raises(expected) as exc_info:
        client.get("https://example.test", {})

    assert type(exc_info.value) is expected  # exact class, not a subclass
    assert exc_info.value.__cause__ is original  # `from e` was used


@pytest.mark.parametrize("status", [200, 201, 204, 299])
def test_success_returns_response(status):
    response = FakeResponse({}, status_code=status)
    client = make_client(StaticSession(response))

    assert client.get("https://example.test", {}) is response


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (600, ex.UnexpectedResponseError),
        (500, ex.NetworkHTTP5xxError),
        (599, ex.NetworkHTTP5xxError),
        (429, ex.RateLimitError),
        (400, ex.HTTPClientError),
        (418, ex.HTTPClientError),
        (399, ex.UnexpectedResponseError),
        (304, ex.UnexpectedResponseError),
        (300, ex.UnexpectedResponseError),
        (199, ex.UnexpectedResponseError),
    ],
)
def test_status_codes_raise(status, expected):
    response = FakeResponse({}, status_code=status)
    client = make_client(StaticSession(response))

    with pytest.raises(expected) as exc_info:
        client.get("https://example.test", {})
    assert type(exc_info.value) is expected


def test_get_json_returns_dict():
    client = make_client(StaticSession(FakeResponse({"a": 1})))

    result = client.get_json("https://example.test", {})

    assert result == {"a": 1}


def test_get_json_invalid_json():
    client = make_client(StaticSession(BadJsonResponse({})))

    with pytest.raises(ex.InvalidJSONError) as exc_info:
        client.get_json("https://example.test", {})

    assert type(exc_info.value) is ex.InvalidJSONError
    assert isinstance(exc_info.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "payload",
    [[1, 2], "text", 42, None],
    ids=["list", "string", "number", "none"],
)
def test_get_json_non_dict(payload):
    client = make_client(StaticSession(FakeResponse(payload)))

    with pytest.raises(ex.InvalidJSONShapeError) as exc_info:
        client.get_json("https://example.test", {})

    assert type(exc_info.value) is ex.InvalidJSONShapeError


@pytest.mark.parametrize(
    ("kwargs", "expected_timeout"),
    [({}, 10), ({"timeout": 3}, 3)],
    ids=["default", "custom"],
)
def test_timeout_is_passed_to_session(kwargs, expected_timeout):
    session = StaticSession(FakeResponse({}))
    client = make_client(session, **kwargs)

    test_url = "https://example.test"
    test_params = {"a": 1}

    client.get(test_url, test_params)

    url, params, timeout = session.calls[0]
    assert url == test_url
    assert params == test_params
    assert timeout == expected_timeout
    assert len(session.calls) == 1


def test_built_session_retries_transient_errors():
    session = network.ApiClient.build_session()
    retry = session.get_adapter("https://example.com").max_retries

    assert retry.total == 3
    assert retry.backoff_factor == 0.5
    assert retry.raise_on_status is False
    assert set(retry.status_forcelist) == {429, 500, 502, 503, 504}


def test_injected_session_is_not_modified():
    session = requests.Session()
    before = session.get_adapter("https://example.com")

    make_client(session)

    assert session.get_adapter("https://example.com") is before
