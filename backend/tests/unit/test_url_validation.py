"""Unit tests for SSRF-safe URL validation."""

from __future__ import annotations

import pytest

from app.core.url_validation import URLValidationError, validate_fetch_url


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/article",
        "http://localhost/news",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.1/internal",
        "file:///etc/passwd",
        "ftp://example.com/article",
    ],
)
def test_validate_fetch_url_rejects_unsafe_targets(url: str) -> None:
    with pytest.raises(URLValidationError):
        validate_fetch_url(url)


def test_validate_fetch_url_accepts_public_https() -> None:
    # Use a literal public IP to avoid DNS dependency in unit tests.
    validate_fetch_url("https://93.184.216.34/article")


def test_validate_fetch_url_rejects_missing_hostname() -> None:
    with pytest.raises(URLValidationError, match="hostname"):
        validate_fetch_url("https:///path")
