import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.user import UpdateUserRequest


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_id_str(self, user_id: str) -> User | None:
        """Look up by the string form of a UUID (e.g. from a JWT sub claim)."""
        try:
            return await self.get_by_id(uuid.UUID(user_id))
        except ValueError:
            return None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def create(self, data: RegisterRequest, hashed_password: str) -> User:
        user = User(
            email=data.email.lower(),
            username=data.username,
            hashed_password=hashed_password,
            native_language=data.native_language,
            target_language=data.target_language,
        )
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def update(self, user: User, data: UpdateUserRequest) -> User:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self._db.commit()
        await self._db.refresh(user)
        return user
