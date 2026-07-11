"""User-facing API error messages — never expose internal configuration."""

from __future__ import annotations

import logging

from openai import OpenAIError

logger = logging.getLogger(__name__)

AI_UNAVAILABLE = "AI service unavailable — please try again later."
SERVICE_UNAVAILABLE = "Service unavailable — please try again later."


def ai_unavailable_detail(exc: OpenAIError) -> str:
    """Return a safe client message for an OpenAI-compatible provider error."""
    from openai import (
        APIConnectionError,
        APITimeoutError,
        AuthenticationError,
        InternalServerError,
        NotFoundError,
        RateLimitError,
    )

    if isinstance(exc, RateLimitError):
        return "AI rate limit reached — wait a minute and try again."
    if isinstance(exc, AuthenticationError):
        logger.error("AI authentication failed — check server API key configuration")
        return AI_UNAVAILABLE
    if isinstance(exc, NotFoundError):
        logger.error("AI model not found — check server model configuration")
        return AI_UNAVAILABLE
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return "AI service timed out — please try again."
    if isinstance(exc, InternalServerError):
        return "AI provider is temporarily overloaded — please try again."
    logger.warning("AI service error: %s", exc)
    return AI_UNAVAILABLE


def service_unavailable_from_runtime(exc: RuntimeError, *, context: str) -> str:
    """Log a RuntimeError and return a generic 503 message."""
    logger.warning("%s: %s", context, exc)
    return SERVICE_UNAVAILABLE
