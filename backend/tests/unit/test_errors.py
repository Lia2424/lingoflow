"""Unit tests for sanitized API error messages."""

from unittest.mock import MagicMock

from openai import AuthenticationError, NotFoundError, RateLimitError

from app.core.errors import AI_UNAVAILABLE, ai_unavailable_detail


def test_ai_unavailable_detail_hides_auth_config() -> None:
    exc = AuthenticationError("bad key", response=MagicMock(), body=None)
    detail = ai_unavailable_detail(exc)
    assert detail == AI_UNAVAILABLE
    assert "OPENAI" not in detail


def test_ai_unavailable_detail_hides_model_config() -> None:
    exc = NotFoundError("missing model", response=MagicMock(), body=None)
    detail = ai_unavailable_detail(exc)
    assert detail == AI_UNAVAILABLE
    assert "model" not in detail.lower() or "unavailable" in detail.lower()


def test_ai_unavailable_detail_keeps_rate_limit_hint() -> None:
    exc = RateLimitError("rate limit", response=MagicMock(), body=None)
    assert "rate limit" in ai_unavailable_detail(exc).lower()
