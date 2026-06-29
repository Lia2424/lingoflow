from pydantic import BaseModel


class ErrorDetail(BaseModel):
    detail: str


class ValidationErrorDetail(BaseModel):
    detail: list[dict]


# Reusable responses= dicts for FastAPI route decorators
RESPONSES_401 = {
    401: {"model": ErrorDetail, "description": "Missing or invalid authentication token"},
}

RESPONSES_403 = {
    403: {"model": ErrorDetail, "description": "Forbidden — insufficient permissions"},
}

RESPONSES_404 = {
    404: {"model": ErrorDetail, "description": "Resource not found"},
}

RESPONSES_409 = {
    409: {"model": ErrorDetail, "description": "Conflict — resource already exists"},
}

RESPONSES_422 = {
    422: {"model": ValidationErrorDetail, "description": "Request body validation failed"},
}

# Convenience combinations
AUTH_RESPONSES = {**RESPONSES_401, **RESPONSES_422}
PROTECTED_RESPONSES = {**RESPONSES_401, **RESPONSES_403, **RESPONSES_422}
