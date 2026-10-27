from contextlib import contextmanager
from collections import defaultdict
from datetime import timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.db import expense_repository as repository, repositories
from app.models import Expense, ExpenseShare
from app.schemas.expenses import ExpenseCreate, ExpenseRead, ExpenseUpdate, ShareRead
from app.services.errors import ConflictError, InputError, NotFoundError
from app.services.groups import get_group
from app.services.money import MAX_AMOUNT, split_equally


@contextmanager
def expense_transaction(session: Session):
    try:
        yield
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("El gasto entra en conflicto con participantes o repartos relacionados.") from None
    except Exception:
        session.rollback()
        raise


def _find(session: Session, group_id: UUID, expense_id: UUID) -> Expense:
    expense = repository.find_expense(session, group_id, expense_id)
    if expense is None:
        raise NotFoundError("Gasto no encontrado en este grupo.")
    return expense


def _read(expense: Expense, shares: list[ExpenseShare]) -> ExpenseRead:
    return ExpenseRead(id=expense.id, group_id=expense.group_id, paid_by=expense.paid_by,
                       description=expense.description, amount=expense.amount, created_at=expense.created_at.astimezone(timezone.utc),
                       shares=[ShareRead(member_id=share.member_id, amount_owed=share.amount_owed)
                               for share in shares if share.expense_id == expense.id])


def list_expenses(session: Session, group_id: UUID, owner_id: UUID) -> list[ExpenseRead]:
    get_group(session, group_id, owner_id, lock=True)
    by_expense = defaultdict(list)
    for share in repository.list_shares(session, group_id):
        by_expense[share.expense_id].append(share)
    return [_read(expense, by_expense[expense.id]) for expense in repository.list_expenses(session, group_id)]


def get_expense(session: Session, group_id: UUID, expense_id: UUID, owner_id: UUID) -> ExpenseRead:
    get_group(session, group_id, owner_id, lock=True)
    return _read(_find(session, group_id, expense_id), repository.list_shares(session, group_id))


def _validate_members(session: Session, group_id: UUID, payload: ExpenseCreate):
    member_ids = {member.id for member in repositories.list_members(session, group_id)}
    if payload.paid_by not in member_ids or not set(payload.participant_ids).issubset(member_ids):
        raise InputError("El pagador y todos los participantes deben pertenecer a este grupo.")


def save_expense(session: Session, group_id: UUID, payload: ExpenseCreate | ExpenseUpdate,
                 owner_id: UUID, expense_id: UUID | None = None) -> ExpenseRead:
    with expense_transaction(session):
        # Serialize writes and balance snapshots per group; prevents lost share updates.
        get_group(session, group_id, owner_id, lock=True)
        previous = repository.list_shares(session, group_id) if expense_id else []
        expense = _find(session, group_id, expense_id) if expense_id else None
        if expense:
            values = {"description": expense.description, "amount": expense.amount, "paid_by": expense.paid_by,
                      "participant_ids": [share.member_id for share in previous if share.expense_id == expense.id]}
            values.update(payload.model_dump(exclude_unset=True))
            values = ExpenseCreate(**values)
        else:
            values = payload
        _validate_members(session, group_id, values)
        if repository.total_amount(session, group_id, excluding=expense_id) + values.amount > MAX_AMOUNT:
            raise InputError("El total del grupo supera el límite de pesos enteros admitido.")
        allocation = split_equally(values.amount, values.participant_ids)
        if expense:
            for share in previous:
                if share.expense_id == expense.id:
                    session.delete(share)
            session.flush()  # Delete old PKs before inserting the replacement shares.
            expense.description, expense.amount, expense.paid_by = values.description, values.amount, values.paid_by
        else:
            expense = Expense(group_id=group_id, description=values.description, amount=values.amount, paid_by=values.paid_by)
        session.add(expense)
        session.flush()
        shares = [ExpenseShare(expense_id=expense.id, group_id=group_id, member_id=member, amount_owed=amount)
                  for member, amount in allocation.items()]
        session.add_all(shares)
        session.flush()
        result = _read(expense, shares)
    return result


def delete_expense(session: Session, group_id: UUID, expense_id: UUID, owner_id: UUID):
    with expense_transaction(session):
        get_group(session, group_id, owner_id, lock=True)
        session.delete(_find(session, group_id, expense_id))
