"""Usuarios, sesiones revocables y propietario opcional para preservar grupos previos."""
from alembic import op
import sqlalchemy as sa

revision = "0002_auth_ownership"
down_revision = "0001_groups_members"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint("email = lower(btrim(email))", name="ck_users_email_normalized"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("token_hash"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.add_column("groups", sa.Column("owner_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_groups_owner_id_users", "groups", "users", ["owner_id"], ["id"])
    op.create_index("ix_groups_owner_id", "groups", ["owner_id"])
    # No backfill arbitrario: grupos/miembros previos se conservan íntegros.


def downgrade():
    raise RuntimeError("Rollback destructivo bloqueado: requiere un plan revisado de conservación de datos.")
