from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Expense, ExpenseShare


def list_expenses(session: Session, group_id: UUID) -> list[Expense]:
    return list(session.exec(select(Expense).where(Expense.group_id == group_id)
                             .order_by(Expense.created_at, Expense.id)).all())


def find_expense(session: Session, group_id: UUID, expense_id: UUID) -> Expense | None:
    return session.exec(select(Expense).where(Expense.id == expense_id, Expense.group_id == group_id)).first()


def list_shares(session: Session, group_id: UUID) -> list[ExpenseShare]:
    return list(session.exec(select(ExpenseShare).where(ExpenseShare.group_id == group_id)
                             .order_by(ExpenseShare.expense_id, ExpenseShare.member_id)).all())


def total_amount(session: Session, group_id: UUID, excluding: UUID | None = None) -> int:
    statement = select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.group_id == group_id)
    if excluding:
        statement = statement.where(Expense.id != excluding)
    return int(session.exec(statement).one())


def member_has_expenses(session: Session, member_id: UUID) -> bool:
    return (session.exec(select(Expense.id).where(Expense.paid_by == member_id).limit(1)).first() is not None or
            session.exec(select(ExpenseShare.expense_id).where(ExpenseShare.member_id == member_id).limit(1)).first() is not None)
