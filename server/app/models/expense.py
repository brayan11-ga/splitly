from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKeyConstraint, UniqueConstraint, func
from sqlmodel import Field, SQLModel


class Expense(SQLModel, table=True):
    __tablename__ = "expenses"
    __table_args__ = (
        UniqueConstraint("id", "group_id", name="uq_expenses_id_group"),
        ForeignKeyConstraint(["paid_by", "group_id"], ["members.id", "members.group_id"], name="fk_expenses_payer_group"),
        CheckConstraint("amount > 0 AND amount <= 9007199254740991", name="ck_expenses_amount"),
        CheckConstraint("length(btrim(description)) BETWEEN 1 AND 240", name="ck_expenses_description"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    group_id: UUID = Field(foreign_key="groups.id", nullable=False, index=True)
    paid_by: UUID = Field(nullable=False, index=True)
    description: str = Field(max_length=240, nullable=False)
    amount: int = Field(sa_column=Column(BigInteger, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )


class ExpenseShare(SQLModel, table=True):
    __tablename__ = "expense_shares"
    __table_args__ = (
        ForeignKeyConstraint(["expense_id", "group_id"], ["expenses.id", "expenses.group_id"],
                             name="fk_shares_expense_group", ondelete="CASCADE"),
        ForeignKeyConstraint(["member_id", "group_id"], ["members.id", "members.group_id"], name="fk_shares_member_group"),
        CheckConstraint("amount_owed >= 0 AND amount_owed <= 9007199254740991", name="ck_shares_amount"),
    )

    expense_id: UUID = Field(primary_key=True)
    member_id: UUID = Field(primary_key=True, index=True)
    group_id: UUID = Field(nullable=False, index=True)
    amount_owed: int = Field(sa_column=Column(BigInteger, nullable=False))
