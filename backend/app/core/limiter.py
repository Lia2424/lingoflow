from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security import decode_token


def get_user_or_ip(request: Request) -> str:
    """Rate-limit key: authenticated user id, else client IP."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = decode_token(auth[7:])
            if payload.get("type") == "access":
                return f"user:{payload['sub']}"
        except Exception:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=get_remote_address)
