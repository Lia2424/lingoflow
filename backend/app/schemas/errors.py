from typing import Any

from pydantic import BaseModel

_ResponsesDict = dict[int | str, dict[str, Any]]


class ErrorDetail(BaseModel):
    detail: str


class ValidationErrorDetail(BaseModel):
    detail: list[dict[str, Any]]


# Reusable responses= dicts for FastAPI route decorators.
RESPONSES_401: _ResponsesDict = {
    401: {
        "model": ErrorDetail,
        "description": "Missing or invalid authentication token",
    },
}

RESPONSES_403: _ResponsesDict = {
    403: {
        "model": ErrorDetail,
        "description": "Forbidden — insufficient permissions",
    },
}

RESPONSES_404: _ResponsesDict = {
    404: {"model": ErrorDetail, "description": "Resource not found"},
}

RESPONSES_409: _ResponsesDict = {
    409: {
        "model": ErrorDetail,
        "description": "Conflict — resource already exists",
    },
}

RESPONSES_422: _ResponsesDict = {
    422: {
        "model": ValidationErrorDetail,
        "description": "Request body validation failed",
    },
}

# Convenience combinations
AUTH_RESPONSES: _ResponsesDict = {**RESPONSES_401, **RESPONSES_422}
PROTECTED_RESPONSES: _ResponsesDict = {
    **RESPONSES_401,
    **RESPONSES_403,
    **RESPONSES_422,
}
