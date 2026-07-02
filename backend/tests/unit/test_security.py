"""Unit tests for JWT and password utilities — no DB required."""

import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_round_trip() -> None:
    hashed = hash_password("hunter2")
    assert verify_password("hunter2", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_decode() -> None:
    token = create_access_token("user-123")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_type() -> None:
    token = create_refresh_token("user-123")
    payload = decode_token(token)
    assert payload["type"] == "refresh"


def test_tampered_token_raises() -> None:
    token = create_access_token("user-123")
    with pytest.raises(jwt.PyJWTError):
        decode_token(token + "tampered")


def test_jti_unique_across_tokens() -> None:
    t1 = create_access_token("user-123")
    t2 = create_access_token("user-123")
    assert decode_token(t1)["jti"] != decode_token(t2)["jti"]


def test_password_over_72_bytes_rejected() -> None:
    from pydantic import ValidationError

    from app.schemas.auth import RegisterRequest

    long_password = "a" * 73
    with pytest.raises(ValidationError, match="72 bytes"):
        RegisterRequest(
            email="a@b.com",
            username="testuser",
            password=long_password,
            native_language="en",
            target_language="es",
        )
