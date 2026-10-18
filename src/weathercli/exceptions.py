class AppError(Exception):
    """Base class for all exceptions in the application."""

    pass


# --- First Level Branches ---
class NetworkError(AppError):
    """Exception raised for network-related errors."""

    pass


class InputError(AppError):
    """Exception raised for invalid user input."""

    pass


class UnexpectedResponseError(AppError):
    """Exception raised for unexpected API responses."""

    pass


# --- Specific Errors ---
class NetworkTimeoutError(NetworkError):
    """Exception raised for network timeouts."""

    pass


class NetworkConnectionError(NetworkError):
    """Exception raised for network connection issues."""

    pass


class NetworkHTTP5xxError(NetworkError):
    """Exception raised for HTTP 5xx errors."""

    pass


class InvalidJSONError(UnexpectedResponseError):
    """Exception raised for invalid JSON responses."""

    pass


class InvalidJSONShapeError(UnexpectedResponseError):
    """Exception raised for unexpected JSON structure."""

    pass


class HTTPClientError(UnexpectedResponseError):
    """Exception raised for HTTP 4xx errors."""

    pass


class RateLimitError(NetworkError):
    """Exception raised when the API rate limit is exceeded."""

    pass


class LocationNotFoundError(InputError):
    """Exception raised when the specified location is not found."""

    pass
