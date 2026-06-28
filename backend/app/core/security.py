from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def _encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return _encode({"sub": subject, "exp": expire, "type": "access"})


def create_refresh_token(subject: str) -> str:
    """Refresh tokens are rotated on every use (sliding session)."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return _encode({"sub": subject, "exp": expire, "type": "refresh"})


def decode_token(token: str) -> dict[str, Any]:
    """Raises jose.JWTError on invalid or expired tokens."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
