"""create content and interactions tables

Revision ID: f0ae2d3faf74
Revises: 6127b555fe71
Create Date: 2026-07-02 20:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f0ae2d3faf74"
down_revision: str | None = "6127b555fe71"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop orphaned types left by any previous partial run (idempotent on a fresh DB).
    op.execute("DROP TYPE IF EXISTS sourcetype")
    op.execute("DROP TYPE IF EXISTS interactionstatus")

    # ── content table ────────────────────────────────────────────────────────
    # sourcetype and interactionstatus are new — SQLAlchemy creates them automatically.
    # cefrlevel already exists from migration 1, so create_type=False avoids a duplicate.
    op.create_table(
        "content",
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "cefr_level",
            sa.Enum(
                "A1",
                "A2",
                "B1",
                "B2",
                "C1",
                "C2",
                name="cefrlevel",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.Enum(
                "article",
                "podcast",
                "youtube",
                "music",
                "tv_show",
                "other",
                name="sourcetype",
            ),
            nullable=False,
        ),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=2048), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_language"), "content", ["language"], unique=False)
    op.create_index(op.f("ix_content_url"), "content", ["url"], unique=True)

    # ── user_content_interactions table ──────────────────────────────────────
    op.create_table(
        "user_content_interactions",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("content_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "saved",
                "in_progress",
                "completed",
                "liked",
                name="interactionstatus",
            ),
            nullable=False,
        ),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["content_id"], ["content.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "content_id", name="uq_user_content"),
    )
    op.create_index(
        op.f("ix_user_content_interactions_content_id"),
        "user_content_interactions",
        ["content_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_content_interactions_user_id"),
        "user_content_interactions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_content_interactions_user_id"),
        table_name="user_content_interactions",
    )
    op.drop_index(
        op.f("ix_user_content_interactions_content_id"),
        table_name="user_content_interactions",
    )
    op.drop_table("user_content_interactions")
    op.drop_index(op.f("ix_content_url"), table_name="content")
    op.drop_index(op.f("ix_content_language"), table_name="content")
    op.drop_table("content")
    sa.Enum(name="interactionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sourcetype").drop(op.get_bind(), checkfirst=True)
