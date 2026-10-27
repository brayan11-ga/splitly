from uuid import UUID

from sqlmodel import Session

from app.db import expense_repository, repositories
from app.schemas.expenses import BalancesRead, MemberBalance
from app.services.groups import get_group
from app.services.money import suggest_transfers


def get_balances(session: Session, group_id: UUID, owner_id: UUID) -> BalancesRead:
    get_group(session, group_id, owner_id, lock=True)
    members = repositories.list_members(session, group_id)
    expenses = expense_repository.list_expenses(session, group_id)
    shares = expense_repository.list_shares(session, group_id)
    paid = {member.id: 0 for member in members}
    owed = dict(paid)
    for expense in expenses:
        paid[expense.paid_by] += expense.amount
    for share in shares:
        owed[share.member_id] += share.amount_owed
    net = {member.id: paid[member.id] - owed[member.id] for member in members}
    return BalancesRead(group_id=group_id, total_amount=sum(paid.values()), expense_count=len(expenses),
                        members=[MemberBalance(member_id=member.id, name=member.name, total_paid=paid[member.id],
                                               total_owed=owed[member.id], net_balance=net[member.id]) for member in members],
                        transfers=suggest_transfers(net))
