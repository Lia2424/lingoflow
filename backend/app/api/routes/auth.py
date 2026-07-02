from fastapi import APIRouter, Body, Request, status

from app.core.dependencies import DatabaseDep
from app.core.limiter import limiter
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.errors import RESPONSES_401, RESPONSES_409, RESPONSES_422
from app.services.auth import AuthService

router = APIRouter()


def _service(db: DatabaseDep) -> AuthService:
    return AuthService(UserRepository(db))


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**RESPONSES_409, **RESPONSES_422},
)
@limiter.limit("5/minute")
async def register(
    request: Request, data: RegisterRequest, db: DatabaseDep
) -> TokenResponse:
    return await _service(db).register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={**RESPONSES_401, **RESPONSES_422},
)
@limiter.limit("10/minute")
async def login(
    request: Request, data: LoginRequest, db: DatabaseDep
) -> TokenResponse:
    return await _service(db).login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={**RESPONSES_401, **RESPONSES_422},
)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    db: DatabaseDep,
    refresh_token: str = Body(..., embed=True),
) -> TokenResponse:
    return await _service(db).refresh(refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    db: DatabaseDep,
    refresh_token: str = Body(..., embed=True),
) -> None:
    await _service(db).logout(refresh_token)
