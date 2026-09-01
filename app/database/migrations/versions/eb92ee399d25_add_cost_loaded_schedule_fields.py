"""add cost-loaded schedule fields

Revision ID: eb92ee399d25
Revises: 109e15655736
Create Date: 2026-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb92ee399d25"
down_revision = "109e15655736"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # project_costs: track whether a row was entered manually or
    # auto-aggregated from an uploaded cost-loaded schedule.
    op.add_column(
        "project_costs",
        sa.Column(
            "source",
            sa.String(length=30),
            nullable=False,
            server_default="manual",
        ),
    )

    # schedule_activities: optional per-activity financial fields,
    # populated when the uploaded workbook contains matching columns.
    op.add_column(
        "schedule_activities",
        sa.Column("budgeted_cost", sa.Float(), nullable=True),
    )
    op.add_column(
        "schedule_activities",
        sa.Column("actual_cost", sa.Float(), nullable=True),
    )
    op.add_column(
        "schedule_activities",
        sa.Column("earned_value", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("schedule_activities", "earned_value")
    op.drop_column("schedule_activities", "actual_cost")
    op.drop_column("schedule_activities", "budgeted_cost")
    op.drop_column("project_costs", "source")
