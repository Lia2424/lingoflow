"""Admin-only routes.

All endpoints are protected by a static pre-shared key supplied in the
``X-Admin-Key`` request header (compared to ``settings.ADMIN_API_KEY``).

These routes are intentionally **not** versioned with the user-facing API
and should never be exposed publicly without a reverse-proxy restriction.
"""

from __future__ import annotations

import secrets
from typing import Annotated, Literal

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.dependencies import DatabaseDep
from app.core.errors import service_unavailable_from_runtime
from app.core.limiter import limiter
from app.services import ingest as ingest_service

router = APIRouter()

_SOURCE_TYPES = Literal["youtube", "podcast"]


def _require_admin_key(x_admin_key: Annotated[str | None, Header()] = None) -> None:
    """Dependency that validates the X-Admin-Key header."""
    if not settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin endpoints are not configured on this server.",
        )
    if not secrets.compare_digest(x_admin_key or "", settings.ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Admin-Key header.",
        )


class IngestRequest(BaseModel):
    source_type: _SOURCE_TYPES = Field(
        description="Content source to ingest from: youtube | podcast"
    )
    language: str = Field(
        min_length=2,
        max_length=10,
        description="BCP-47 language code (e.g. 'es', 'fr-FR')",
    )
    query: str = Field(
        min_length=1,
        max_length=500,
        description="YouTube search query or iTunes podcast show name.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Maximum items to fetch.",
    )


class IngestResponse(BaseModel):
    source_type: str
    language: str
    query: str
    total_fetched: int
    created: int
    updated: int
    errors: int


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger a manual content ingestion run",
    responses={
        401: {"description": "Invalid or missing X-Admin-Key"},
        503: {"description": "Admin endpoints not configured"},
    },
)
@limiter.limit("5/minute")
async def trigger_ingest(
    request: Request,
    body: IngestRequest,
    db: DatabaseDep,
    x_admin_key: Annotated[str | None, Header()] = None,
) -> IngestResponse:
    """Seed the content table from YouTube or iTunes/RSS podcasts."""
    _require_admin_key(x_admin_key)

    try:
        if body.source_type == "youtube":
            result = await ingest_service.ingest_youtube(
                db, body.language, body.query, body.limit
            )
        else:
            result = await ingest_service.ingest_podcasts(
                db, body.language, body.query, body.limit
            )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=service_unavailable_from_runtime(exc, context="admin ingest"),
        ) from exc

    return IngestResponse(
        source_type=result.source_type,
        language=result.language,
        query=result.query,
        total_fetched=result.total_fetched,
        created=result.created,
        updated=result.updated,
        errors=result.errors,
    )
