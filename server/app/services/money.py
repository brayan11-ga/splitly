"""Pure integer COP calculations; independent of HTTP and persistence."""
from uuid import UUID

MAX_AMOUNT = 9_007_199_254_740_991  # Also exactly representable by the JS client.


def split_equally(amount: int, participant_ids: list[UUID]) -> dict[UUID, int]:
    if type(amount) is not int or not 0 < amount <= MAX_AMOUNT:
        raise ValueError("El importe debe ser un entero positivo en COP.")
    if not participant_ids or len(set(participant_ids)) != len(participant_ids):
        raise ValueError("El reparto requiere participantes únicos.")
    ordered = sorted(participant_ids, key=str)
    quotient, remainder = divmod(amount, len(ordered))
    return {member_id: quotient + (index < remainder) for index, member_id in enumerate(ordered)}


def suggest_transfers(balances: dict[UUID, int]) -> list[dict]:
    """Stable UUID matching; no claim of globally minimal transfer count."""
    if sum(balances.values()) != 0:
        raise ValueError("Los balances deben sumar cero.")
    debtors = [[member, -value] for member, value in sorted(balances.items(), key=lambda pair: str(pair[0])) if value < 0]
    creditors = [[member, value] for member, value in sorted(balances.items(), key=lambda pair: str(pair[0])) if value > 0]
    transfers = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        amount = min(debtors[i][1], creditors[j][1])
        transfers.append({"from_member_id": debtors[i][0], "to_member_id": creditors[j][0], "amount": amount})
        debtors[i][1] -= amount
        creditors[j][1] -= amount
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return transfers
