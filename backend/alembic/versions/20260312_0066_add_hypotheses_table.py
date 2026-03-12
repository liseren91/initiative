"""Add hypotheses table.

Revision ID: 20260312_0066
Revises: 20260301_0065
Create Date: 2026-03-12
"""

from alembic import op
import sqlalchemy as sa

revision = "20260312_0066"
down_revision = "20260301_0065"
branch_labels = None
depends_on = None

IS_SUPER = "current_setting('app.is_superadmin', true) = 'true'"


def upgrade() -> None:
    hypothesis_status = sa.Enum(
        "idea", "evaluation", "research", "decision",
        "project", "rejected", "paused",
        name="hypothesis_status",
    )
    hypothesis_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "hypotheses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("guild_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "status",
            hypothesis_status,
            nullable=False,
            server_default="idea",
        ),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["guild_id"], ["guilds.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hypotheses_guild_id", "hypotheses", ["guild_id"])
    op.create_index("ix_hypotheses_status", "hypotheses", ["status"])

    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE hypotheses ENABLE ROW LEVEL SECURITY"))
    conn.execute(sa.text("ALTER TABLE hypotheses FORCE ROW LEVEL SECURITY"))
    conn.execute(sa.text(f"""
        CREATE POLICY guild_isolation ON hypotheses
        FOR ALL
        USING (
            guild_id = current_setting('app.current_guild_id', true)::int
            OR {IS_SUPER}
        )
        WITH CHECK (
            guild_id = current_setting('app.current_guild_id', true)::int
            OR {IS_SUPER}
        )
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP POLICY IF EXISTS guild_isolation ON hypotheses"))
    conn.execute(sa.text("ALTER TABLE hypotheses DISABLE ROW LEVEL SECURITY"))
    op.drop_index("ix_hypotheses_status", table_name="hypotheses")
    op.drop_index("ix_hypotheses_guild_id", table_name="hypotheses")
    op.drop_table("hypotheses")
    sa.Enum(name="hypothesis_status").drop(op.get_bind(), checkfirst=True)
