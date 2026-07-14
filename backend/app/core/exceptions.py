class AppException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class UnauthorizedException(AppException):
    """Raised when a request lacks valid authentication."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """Raised when a user lacks permission for an action."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status_code=403)


class ValidationException(AppException):
    """Raised when input validation fails outside of Pydantic's own checks."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=422)