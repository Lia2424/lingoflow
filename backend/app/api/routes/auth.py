from fastapi import APIRouter, Body, status

from app.core.dependencies import DatabaseDep
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter()


def _service(db: DatabaseDep) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DatabaseDep) -> TokenResponse:
    return await _service(db).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DatabaseDep) -> TokenResponse:
    return await _service(db).login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: DatabaseDep = ...,
) -> TokenResponse:
    return await _service(db).refresh(refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(refresh_token: str = Body(..., embed=True)) -> None:
    # Token is discarded client-side; server-side blocklist added in Milestone 6.
    pass
