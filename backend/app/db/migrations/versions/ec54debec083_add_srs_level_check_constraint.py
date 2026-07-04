"""add srs_level check constraint

Revision ID: ec54debec083
Revises: 333dcf494918
Create Date: 2026-07-04 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ec54debec083"
down_revision: str | None = "333dcf494918"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_vocabulary_entries_srs_level_range",
        "vocabulary_entries",
        sa.text("srs_level >= 0 AND srs_level <= 5"),
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_vocabulary_entries_srs_level_range",
        "vocabulary_entries",
        type_="check",
    )
