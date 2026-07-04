import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class VocabularyEntry(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "vocabulary_entries"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Nullable — word may be saved independently of any content item.
    content_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content.id", ondelete="SET NULL"), nullable=True, index=True
    )
    word: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Spaced-repetition state (SM-2 inspired).
    # 0 = unseen / just added; 5 = fully mastered.
    srs_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Null means "due immediately" (newly added, never reviewed).
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    __table_args__ = (
        # A user cannot save the exact same word (case-sensitive) twice for
        # the same language. Frees the UI from needing a separate check.
        UniqueConstraint("user_id", "word", "language", name="uq_user_word_language"),
    )
