from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDMixin


class ContentQuestion(UUIDMixin, Base):
    """A cached AI-generated multiple-choice comprehension question.

    Questions are generated on first request and cached here so the AI is not
    called again for the same content item.  ``answer_index`` is 0-based into
    the ``options`` array.
    """

    __tablename__ = "content_questions"

    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    # ["Option A", "Option B", "Option C", "Option D"]
    options: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    answer_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
