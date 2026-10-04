"""Create exception, evidence, and review event tables.

Revision ID: 0001
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "exceptions",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(length=80), nullable=False),
        sa.Column("household", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("description", sa.String(length=240), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("age", sa.String(length=24), nullable=False),
        sa.Column("display_value", sa.String(length=32), nullable=False),
        sa.Column("rule", sa.String(length=240), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("checklist", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "category IN ('Position mismatch', 'Cash variance', "
            "'Unmatched security', 'Stale record')",
            name="ck_exceptions_category",
        ),
        sa.CheckConstraint(
            "priority IN ('High', 'Medium', 'Low')", name="ck_exceptions_priority"
        ),
        sa.CheckConstraint(
            "status IN ('Open', 'Investigating', 'Resolved', 'Dismissed')",
            name="ck_exceptions_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("display_order"),
    )
    op.create_table(
        "evidence_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exception_id", sa.String(length=32), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("quantity", sa.String(length=32), nullable=False),
        sa.Column("value", sa.String(length=32), nullable=False),
        sa.Column("as_of", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.CheckConstraint(
            "side IN ('internal', 'external')", name="ck_evidence_side"
        ),
        sa.ForeignKeyConstraint(
            ["exception_id"], ["exceptions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "exception_id", "side", name="uq_evidence_exception_side"
        ),
    )
    op.create_index(
        "ix_evidence_records_exception_id",
        "evidence_records",
        ["exception_id"],
    )
    op.create_table(
        "review_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exception_id", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=24), nullable=False),
        sa.Column("previous_status", sa.String(length=24), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=True),
        sa.Column("message", sa.String(length=240), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "event_type IN ('detected', 'status_changed')",
            name="ck_review_events_type",
        ),
        sa.CheckConstraint(
            "status IS NULL OR status IN "
            "('Open', 'Investigating', 'Resolved', 'Dismissed')",
            name="ck_review_events_status",
        ),
        sa.ForeignKeyConstraint(
            ["exception_id"], ["exceptions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_review_events_exception_id",
        "review_events",
        ["exception_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_review_events_exception_id", table_name="review_events")
    op.drop_table("review_events")
    op.drop_index("ix_evidence_records_exception_id", table_name="evidence_records")
    op.drop_table("evidence_records")
    op.drop_table("exceptions")
