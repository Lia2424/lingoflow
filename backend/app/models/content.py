from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enum_utils import enum_values
from app.models.enums import CEFRLevel, SourceType


class Content(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "content"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(
        String(2048), unique=True, nullable=False, index=True
    )
    # Canonical ID on the source platform (e.g. "youtube:dQw4w9WgXcQ").
    # Used to deduplicate ingested content without relying on URL variations.
    external_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    source_type: Mapped[SourceType] = mapped_column(
        SAEnum(SourceType, name="sourcetype", values_callable=enum_values),
        nullable=False,
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    cefr_level: Mapped[CEFRLevel] = mapped_column(
        SAEnum(CEFRLevel, name="cefrlevel", values_callable=enum_values),
        nullable=False,
    )
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
