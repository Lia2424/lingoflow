import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import InteractionStatus


class UserContentInteraction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_content_interactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("content.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[InteractionStatus] = mapped_column(
        SAEnum(
            InteractionStatus,
            name="interactionstatus",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    # 1–5 star rating; null means not yet rated
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="uq_user_content"),
    )
