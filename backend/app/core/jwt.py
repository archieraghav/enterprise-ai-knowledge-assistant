from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt

from app.core.config import settings


def _create_token(subject: str, expires_delta: timedelta, token_type: Literal["access", "refresh"]) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": token_type,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    """Create a short-lived access token for API authentication."""
    expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return _create_token(subject, expires_delta, "access")


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token used to obtain new access tokens."""
    expires_delta = timedelta(days=settings.jwt_refresh_token_expire_days)
    return _create_token(subject, expires_delta, "refresh")


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT, returning its payload or None if invalid/expired."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None