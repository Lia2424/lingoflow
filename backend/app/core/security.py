import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import bcrypt
from jose import jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _encode(payload: dict[str, Any]) -> str:
    return cast(str, jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM))


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _encode(
        {"sub": subject, "exp": expire, "type": "access", "jti": str(uuid.uuid4())}
    )


def create_refresh_token(subject: str) -> str:
    """Refresh tokens are rotated on every use (sliding session)."""
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _encode(
        {"sub": subject, "exp": expire, "type": "refresh", "jti": str(uuid.uuid4())}
    )


def decode_token(token: str) -> dict[str, Any]:
    """Raises jose.JWTError on invalid or expired tokens."""
    return cast(
        dict[str, Any],
        jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM]),
    )
