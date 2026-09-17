"""initial_tables

Revision ID: e4b200a03265
Revises:
Create Date: 2026-09-18 01:10:57.156703

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e4b200a03265"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Tüm temel tabloları oluştur."""

    # --- jobs ---
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("company", sa.String(length=256), nullable=False),
        sa.Column("location", sa.String(length=256), nullable=True),
        sa.Column("remote_type", sa.String(length=16), nullable=False, server_default="unknown"),
        sa.Column("requirements", postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("description_raw", sa.Text(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="discovered"),
        sa.Column("posted_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_url", "jobs", ["url"], unique=True)

    # --- match_results ---
    op.create_table(
        "match_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("matched_keywords", postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("gaps", postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("agent_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_match_results_job_id", "match_results", ["job_id"])

    # --- cover_letters ---
    op.create_table(
        "cover_letters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("draft_text", sa.Text(), nullable=False),
        sa.Column("used_context_ids", postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_cover_letters_job_id", "cover_letters", ["job_id"])

    # --- application_status_logs ---
    op.create_table(
        "application_status_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("previous_status", sa.String(length=32), nullable=True),
        sa.Column("new_status", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_application_status_logs_job_id", "application_status_logs", ["job_id"])


def downgrade() -> None:
    """Tüm tabloları sil."""
    op.drop_table("application_status_logs")
    op.drop_table("cover_letters")
    op.drop_table("match_results")
    op.drop_table("jobs")
