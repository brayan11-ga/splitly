"""Gastos y repartos en pesos COP enteros; conserva todas las filas existentes."""
from alembic import op
import sqlalchemy as sa

revision = "0003_expenses_cop"
down_revision = "0002_auth_ownership"
branch_labels = None
depends_on = None


def upgrade():
    # The existing PK guarantees uniqueness; this additional key supports
    # composite FKs that enforce group membership, without backfilling/deleting.
    op.create_unique_constraint("uq_members_id_group", "members", ["id", "group_id"])
    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("paid_by", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(240), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", "group_id", name="uq_expenses_id_group"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["paid_by", "group_id"], ["members.id", "members.group_id"], name="fk_expenses_payer_group"),
        sa.CheckConstraint("amount > 0 AND amount <= 9007199254740991", name="ck_expenses_amount"),
        sa.CheckConstraint("length(btrim(description)) BETWEEN 1 AND 240", name="ck_expenses_description"),
    )
    op.create_index("ix_expenses_group_id", "expenses", ["group_id"])
    op.create_index("ix_expenses_paid_by", "expenses", ["paid_by"])
    op.create_table(
        "expense_shares",
        sa.Column("expense_id", sa.Uuid(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("amount_owed", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("expense_id", "member_id"),
        sa.ForeignKeyConstraint(["expense_id", "group_id"], ["expenses.id", "expenses.group_id"],
                                name="fk_shares_expense_group", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id", "group_id"], ["members.id", "members.group_id"], name="fk_shares_member_group"),
        sa.CheckConstraint("amount_owed >= 0 AND amount_owed <= 9007199254740991", name="ck_shares_amount"),
    )
    op.create_index("ix_expense_shares_member_id", "expense_shares", ["member_id"])
    op.create_index("ix_expense_shares_group_id", "expense_shares", ["group_id"])
    # A cross-row sum cannot be a CHECK. Validate both sides at transaction end,
    # allowing atomic replacement of the shares during PATCH. No SECURITY DEFINER.
    op.execute("""
        CREATE FUNCTION splitly_validate_expense_shares() RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
            affected uuid[];
            expense_key uuid;
            expected bigint;
            assigned numeric;
            share_count bigint;
        BEGIN
            IF TG_TABLE_NAME = 'expenses' THEN
                IF TG_OP = 'INSERT' THEN affected := ARRAY[NEW.id];
                ELSIF TG_OP = 'DELETE' THEN affected := ARRAY[OLD.id];
                ELSE affected := ARRAY[OLD.id, NEW.id]; END IF;
            ELSE
                IF TG_OP = 'INSERT' THEN affected := ARRAY[NEW.expense_id];
                ELSIF TG_OP = 'DELETE' THEN affected := ARRAY[OLD.expense_id];
                ELSE affected := ARRAY[OLD.expense_id, NEW.expense_id]; END IF;
            END IF;
            FOREACH expense_key IN ARRAY affected LOOP
                SELECT amount INTO expected FROM expenses WHERE id = expense_key FOR UPDATE;
                IF FOUND THEN
                    SELECT COALESCE(sum(amount_owed), 0), count(*) INTO assigned, share_count
                    FROM expense_shares WHERE expense_id = expense_key;
                    IF share_count = 0 OR assigned <> expected THEN
                        RAISE EXCEPTION 'El reparto debe tener participantes y sumar exactamente el gasto'
                            USING ERRCODE = '23514';
                    END IF;
                END IF;
            END LOOP;
            RETURN NULL;
        END;
        $$
    """)
    for table in ("expenses", "expense_shares"):
        op.execute(f"""
            CREATE CONSTRAINT TRIGGER ck_{table}_allocation
            AFTER INSERT OR UPDATE OR DELETE ON {table}
            DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
            EXECUTE FUNCTION splitly_validate_expense_shares()
        """)


def downgrade():
    raise RuntimeError("Rollback destructivo bloqueado: requiere un plan revisado de conservación de gastos.")
