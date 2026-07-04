"""create vocabulary_entries table

Revision ID: 333dcf494918
Revises: f0ae2d3faf74
Create Date: 2026-07-04 13:43:02.488133

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "333dcf494918"
down_revision: str | None = "f0ae2d3faf74"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_entries",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("content_id", sa.UUID(), nullable=True),
        sa.Column("word", sa.String(length=200), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("definition", sa.Text(), nullable=True),
        sa.Column("translation", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("srs_level", sa.Integer(), nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["content_id"], ["content.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "word", "language", name="uq_user_word_language"
        ),
    )
    op.create_index(
        op.f("ix_vocabulary_entries_content_id"),
        "vocabulary_entries",
        ["content_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_vocabulary_entries_next_review_at"),
        "vocabulary_entries",
        ["next_review_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_vocabulary_entries_user_id"),
        "vocabulary_entries",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_vocabulary_entries_user_id"), table_name="vocabulary_entries"
    )
    op.drop_index(
        op.f("ix_vocabulary_entries_next_review_at"),
        table_name="vocabulary_entries",
    )
    op.drop_index(
        op.f("ix_vocabulary_entries_content_id"), table_name="vocabulary_entries"
    )
    op.drop_table("vocabulary_entries")
