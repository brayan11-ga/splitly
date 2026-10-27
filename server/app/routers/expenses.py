from uuid import UUID

from fastapi import APIRouter, Response

from app.routers.auth_dependencies import CurrentUser
from app.routers.dependencies import SessionDep
from app.schemas.expenses import BalancesRead, ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.services import balances, expenses

router = APIRouter(prefix="/groups/{group_id}", tags=["expenses"])


@router.post("/expenses", response_model=ExpenseRead, status_code=201)
def create_expense(group_id: UUID, payload: ExpenseCreate, session: SessionDep, user: CurrentUser):
    return expenses.save_expense(session, group_id, payload, user.id)


@router.get("/expenses", response_model=list[ExpenseRead])
def list_expenses(group_id: UUID, session: SessionDep, user: CurrentUser):
    return expenses.list_expenses(session, group_id, user.id)


@router.get("/expenses/{expense_id}", response_model=ExpenseRead)
def get_expense(group_id: UUID, expense_id: UUID, session: SessionDep, user: CurrentUser):
    return expenses.get_expense(session, group_id, expense_id, user.id)


@router.patch("/expenses/{expense_id}", response_model=ExpenseRead)
def update_expense(group_id: UUID, expense_id: UUID, payload: ExpenseUpdate, session: SessionDep, user: CurrentUser):
    return expenses.save_expense(session, group_id, payload, user.id, expense_id)


@router.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(group_id: UUID, expense_id: UUID, session: SessionDep, user: CurrentUser):
    expenses.delete_expense(session, group_id, expense_id, user.id)
    return Response(status_code=204)


@router.get("/balances", response_model=BalancesRead)
def get_balances(group_id: UUID, session: SessionDep, user: CurrentUser):
    return balances.get_balances(session, group_id, user.id)
