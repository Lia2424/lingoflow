"""add external_id to content

Revision ID: a6a2b8699042
Revises: ec54debec083
Create Date: 2026-07-05 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a6a2b8699042"
down_revision: str | None = "ec54debec083"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "content",
        sa.Column("external_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_content_external_id"), "content", ["external_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_content_external_id"), table_name="content")
    op.drop_column("content", "external_id")
