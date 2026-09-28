class FintablesError(Exception):
    """Base exception for fintables."""


class AuthError(FintablesError):
    """Raised when authentication fails or token is missing/expired."""


class NotFoundError(FintablesError):
    """Raised when the requested resource (e.g. company, symbol) is not found."""


class APIError(FintablesError):
    """Raised when API returns an unexpected error."""

    def __init__(self, message: str, status_code: int | None = None, response_text: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text
