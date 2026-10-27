from random import Random
from uuid import UUID

import pytest

from app.services.money import MAX_AMOUNT, split_equally, suggest_transfers


def test_exact_and_deterministic_remainders():
    ids = [UUID(int=3), UUID(int=1), UUID(int=2)]
    assert list(split_equally(100, ids).values()) == [34, 33, 33]
    assert split_equally(100, ids) == split_equally(100, list(reversed(ids)))
    assert list(split_equally(90000, ids).values()) == [30000, 30000, 30000]
    assert list(split_equally(1, ids).values()) == [1, 0, 0]


@pytest.mark.parametrize("amount,ids", [(0, [UUID(int=1)]), (-1, [UUID(int=1)]),
    (1.5, [UUID(int=1)]), (True, [UUID(int=1)]), (MAX_AMOUNT + 1, [UUID(int=1)]),
    (10, []), (10, [UUID(int=1), UUID(int=1)])])
def test_invalid_splits(amount, ids):
    with pytest.raises(ValueError):
        split_equally(amount, ids)


def test_varied_integer_splits_and_settlements():
    rng = Random(4821)
    for count in range(1, 50):
        ids = [UUID(int=i + 1) for i in range(count)]
        for amount in [1, count, count + 1, rng.randint(1, 10**9), MAX_AMOUNT]:
            shares = split_equally(amount, ids)
            assert sum(shares.values()) == amount
            assert max(shares.values()) - min(shares.values()) <= 1
            balances = {member: -owed for member, owed in shares.items()}
            balances[ids[-1]] += amount
            transfers = suggest_transfers(balances)
            assert transfers == suggest_transfers(dict(reversed(list(balances.items()))))
            for transfer in transfers:
                assert transfer['amount'] > 0
                balances[transfer['from_member_id']] += transfer['amount']
                balances[transfer['to_member_id']] -= transfer['amount']
            assert set(balances.values()) == {0}
    with pytest.raises(ValueError):
        suggest_transfers({UUID(int=1): 1})
