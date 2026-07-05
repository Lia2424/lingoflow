"""create content_questions table

Revision ID: b7ad15c9aa1d
Revises: a6a2b8699042
Create Date: 2026-07-05 20:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7ad15c9aa1d"
down_revision: str | None = "a6a2b8699042"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "content_questions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "content_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("answer_index", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        op.f("ix_content_questions_content_id"),
        "content_questions",
        ["content_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_content_questions_content_id"), table_name="content_questions"
    )
    op.drop_table("content_questions")
