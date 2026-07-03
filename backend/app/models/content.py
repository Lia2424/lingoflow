from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import CEFRLevel, SourceType


class Content(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "content"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(
        String(2048), unique=True, nullable=False, index=True
    )
    source_type: Mapped[SourceType] = mapped_column(
        SAEnum(SourceType, name="sourcetype"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    cefr_level: Mapped[CEFRLevel] = mapped_column(
        SAEnum(CEFRLevel, name="cefrlevel"), nullable=False
    )
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
