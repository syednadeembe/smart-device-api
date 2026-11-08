"""JWT validation and short-lived demo-token creation for the API."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import InvalidTokenError


JWT_ALGORITHM = "HS256"
DEFAULT_ISSUER = "smart-device-api"
DEFAULT_AUDIENCE = "smart-device-dashboard"


class TokenRejected(ValueError):
    """Raised when the request does not contain a valid bearer token."""


def _secret() -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters")
    return secret


def issuer() -> str:
    return os.environ.get("JWT_ISSUER", DEFAULT_ISSUER)


def audience() -> str:
    return os.environ.get("JWT_AUDIENCE", DEFAULT_AUDIENCE)


def validate_configuration() -> None:
    """Fail at startup when JWT mode has no usable signing key."""
    _secret()


def validate_bearer_token(authorization: str | None) -> dict[str, Any]:
    if not authorization:
        raise TokenRejected("A Bearer token is required.")

    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise TokenRejected("Use the Authorization: Bearer <token> format.")

    try:
        claims = jwt.decode(
            token.strip(),
            _secret(),
            algorithms=[JWT_ALGORITHM],
            issuer=issuer(),
            audience=audience(),
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except (InvalidTokenError, RuntimeError) as error:
        raise TokenRejected("The token is invalid or expired.") from error

    return claims


def create_demo_token(subject: str, lifetime_seconds: int = 300) -> str:
    if not subject.strip():
        raise ValueError("The token subject must not be empty")
    if not 1 <= lifetime_seconds <= 3600:
        raise ValueError("Token lifetime must be between 1 and 3600 seconds")

    now = datetime.now(timezone.utc)
    claims = {
        "iss": issuer(),
        "aud": audience(),
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(seconds=lifetime_seconds),
    }
    return jwt.encode(claims, _secret(), algorithm=JWT_ALGORITHM)
