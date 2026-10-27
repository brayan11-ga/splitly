from uuid import UUID, uuid4
from unittest.mock import patch

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Expense, ExpenseShare, Group, Member, User
from app.services.money import MAX_AMOUNT


def plan(client):
    group = client.post('/api/groups', json={'name': 'Plan COP'}).json()
    base = f"/api/groups/{group['id']}"
    members = [client.post(base + '/members', json={'name': name}).json() for name in ['Ana', 'Pedro', 'Laura']]
    payload = {'description': 'Cena', 'amount': 90000, 'paid_by': members[0]['id'],
               'participant_ids': [member['id'] for member in members]}
    return base, members, payload


def test_expense_crud_and_balances(api_client):
    base, members, payload = plan(api_client)
    path = base + '/expenses'
    assert api_client.get(path).json() == []
    assert api_client.get(base + '/balances').json()['total_amount'] == 0
    response = api_client.post(path, json={**payload, 'description': ' Cena '})
    assert response.status_code == 201
    expense = response.json()
    assert expense['description'] == 'Cena'
    assert sum(share['amount_owed'] for share in expense['shares']) == 90000
    assert all(share['amount_owed'] == 30000 for share in expense['shares'])
    assert api_client.get(path).json() == [expense]
    assert api_client.get(path + '/' + expense['id']).json() == expense
    balance = api_client.get(base + '/balances').json()
    assert [member['net_balance'] for member in balance['members']] == [60000, -30000, -30000]
    assert sum(member['net_balance'] for member in balance['members']) == 0
    assert len(balance['transfers']) == 2
    for member in members:
        assert api_client.delete(base + '/members/' + member['id']).status_code == 409
    response = api_client.patch(path + '/' + expense['id'], json={
        'amount': 100, 'paid_by': members[1]['id'], 'participant_ids': [members[0]['id'], members[2]['id']],
    })
    assert response.status_code == 200
    assert [share['amount_owed'] for share in response.json()['shares']] == [50, 50]
    assert response.json()['created_at'] == expense['created_at']
    assert api_client.get(base + '/balances').json()['total_amount'] == 100
    assert api_client.patch(path + '/' + expense['id'], json={'description': 'Nuevo'}).json()['amount'] == 100
    assert api_client.delete(path + '/' + expense['id']).status_code == 204
    assert api_client.get(path + '/' + expense['id']).status_code == 404
    assert api_client.get(path).json() == []
    assert api_client.get(base + '/balances').json()['transfers'] == []
    for member in members:
        assert api_client.delete(base + '/members/' + member['id']).status_code == 204


def test_odd_amounts_and_multiple_expenses(api_client):
    base, members, payload = plan(api_client)
    expense = api_client.post(base + '/expenses', json={**payload, 'amount': 101}).json()
    expected = {member: 34 if i < 2 else 33 for i, member in enumerate(sorted(payload['participant_ids']))}
    assert {share['member_id']: share['amount_owed'] for share in expense['shares']} == expected
    assert api_client.post(base + '/expenses', json={**payload, 'amount': 1, 'paid_by': members[1]['id']}).status_code == 201
    result = api_client.get(base + '/balances').json()
    assert result['total_amount'] == 102 and result['expense_count'] == 2
    net = {member['member_id']: member['net_balance'] for member in result['members']}
    assert sum(net.values()) == 0
    for transfer in result['transfers']:
        net[transfer['from_member_id']] += transfer['amount']
        net[transfer['to_member_id']] -= transfer['amount']
    assert set(net.values()) == {0}


@pytest.mark.parametrize('changes', [
    {'amount': 0}, {'amount': -10}, {'amount': 1.5}, {'amount': True}, {'amount': '90000'}, {'amount': MAX_AMOUNT + 1},
    {'description': ''}, {'description': '   '}, {'description': 123}, {'description': 'x' * 241},
    {'participant_ids': []}, {'participant_ids': None}, {'paid_by': None}, {'owner_id': str(uuid4())},
])
def test_expense_invalid_payloads_do_not_change_data(api_client, changes):
    base, _, payload = plan(api_client)
    path = base + '/expenses'
    expense = api_client.post(path, json=payload).json()
    assert api_client.post(path, json={**payload, **changes}).status_code == 422
    assert api_client.patch(path + '/' + expense['id'], json=changes).status_code == 422
    assert api_client.get(path).json() == [expense]


def test_bad_members_duplicate_null_empty_patch_and_group_scope(api_client):
    base, members, payload = plan(api_client)
    other, other_members, _ = plan(api_client)
    path = base + '/expenses'
    for changes in [{'paid_by': other_members[0]['id']}, {'participant_ids': [other_members[0]['id']]},
                    {'paid_by': str(uuid4())}, {'participant_ids': [str(uuid4())]},
                    {'participant_ids': [members[0]['id'], members[0]['id']]}]:
        assert api_client.post(path, json={**payload, **changes}).status_code == 422
    expense = api_client.post(path, json=payload).json()
    for changes in [{}, {'description': None}, {'participant_ids': [other_members[0]['id']]}]:
        assert api_client.patch(path + '/' + expense['id'], json=changes).status_code == 422
    for method in ['get', 'patch', 'delete']:
        kwargs = {'json': {'amount': 10}} if method == 'patch' else {}
        assert getattr(api_client, method)(other + '/expenses/' + expense['id'], **kwargs).status_code == 404
    assert api_client.get(path).json() == [expense]


def test_expense_auth_csrf_and_ownership(api_client):
    base, _, payload = plan(api_client)
    path = base + '/expenses'
    expense = api_client.post(path, json=payload).json()
    detail = path + '/' + expense['id']
    assert api_client.post(path, json=payload, headers={'X-CSRF-Token': 'wrong'}).status_code == 403
    assert api_client.patch(detail, json={'amount': 1}, headers={'Origin': 'https://evil.example'}).status_code == 403
    assert api_client.delete(detail, headers={'X-CSRF-Token': ''}).status_code == 403
    response = api_client.post('/api/auth/register', json={
        'full_name': 'Otro', 'email': f'{uuid4().hex}@example.com', 'password': 'Otra frase de prueba segura 123',
    })
    api_client.headers['X-CSRF-Token'] = response.json()['csrf_token']
    for method, route, kwargs in [('get', path, {}), ('get', detail, {}), ('get', base + '/balances', {}),
                                  ('post', path, {'json': payload}), ('patch', detail, {'json': {'amount': 1}}), ('delete', detail, {})]:
        assert getattr(api_client, method)(route, **kwargs).status_code == 404
    api_client.cookies.clear()
    for method, route, kwargs in [('get', path, {}), ('get', detail, {}), ('get', base + '/balances', {}),
                                  ('post', path, {'json': payload}), ('patch', detail, {'json': {'amount': 1}}), ('delete', detail, {})]:
        assert getattr(api_client, method)(route, **kwargs).status_code == 401


def test_group_total_safe_integer_limit(api_client):
    base, members, payload = plan(api_client)
    payload.update(amount=MAX_AMOUNT, participant_ids=[members[0]['id']])
    created = api_client.post(base + '/expenses', json=payload)
    assert created.status_code == 201
    assert api_client.post(base + '/expenses', json={**payload, 'amount': 1}).status_code == 422
    assert api_client.get(base + '/balances').json()['total_amount'] == MAX_AMOUNT


def test_database_constraints_and_atomic_rollback(api_client, db_connection):
    base, members, payload = plan(api_client)
    group_id = UUID(base.split('/')[3])
    other, other_members, _ = plan(api_client)
    expense = api_client.post(base + '/expenses', json=payload).json()
    expense_id = UUID(expense['id'])
    with Session(db_connection, join_transaction_mode='create_savepoint') as session:
        # Force pending deferred checks, which normal API transactions run at COMMIT.
        session.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
        session.commit()
        for values in [
            dict(expense_id=expense_id, member_id=UUID(members[0]['id']), group_id=group_id, amount_owed=30000),
            dict(expense_id=expense_id, member_id=UUID(other_members[0]['id']), group_id=group_id, amount_owed=1),
        ]:
            session.add(ExpenseShare(**values))
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()
        # Updating a single share without adjusting the expense is rejected.
        share = session.get(ExpenseShare, (expense_id, UUID(members[0]['id'])))
        share.amount_owed = 1
        session.add(share)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        current = session.get(Expense, expense_id)
        assert current.amount == 90000
        assert session.get(ExpenseShare, (expense_id, UUID(members[0]['id']))).amount_owed == 30000
        # A payer from another group cannot be persisted even by bypassing the API.
        current.paid_by = UUID(other_members[0]['id'])
        session.add(current)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_real_commit_enforces_sum_and_persists(postgres_engine):
    # Independent connections prove actual commit, not just fixture savepoints.
    with Session(postgres_engine) as session:
        user = User(full_name='Demo', email=f'{uuid4().hex}@example.com', hashed_password='fixture')
        session.add(user); session.flush()
        group = Group(name='Commit', owner_id=user.id)
        session.add(group); session.flush()
        member = Member(name='Ana', group_id=group.id)
        session.add(member); session.commit()
        group_id, member_id = group.id, member.id
        invalid = Expense(group_id=group_id, paid_by=member_id, description='Sin reparto', amount=10)
        session.add(invalid)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        expense = Expense(group_id=group_id, paid_by=member_id, description='Persistido', amount=10)
        session.add(expense); session.flush()
        session.add(ExpenseShare(expense_id=expense.id, group_id=group_id, member_id=member_id, amount_owed=10))
        expense_id = expense.id
        session.commit()
    with Session(postgres_engine) as session:
        assert session.get(Expense, expense_id).amount == 10
        session.delete(session.get(Expense, expense_id))
        session.commit()
        assert session.exec(select(ExpenseShare).where(ExpenseShare.expense_id == expense_id)).all() == []


def test_failed_share_insert_rolls_back_whole_create_and_edit(api_client):
    base, _, payload = plan(api_client)
    path = base + '/expenses'
    original = api_client.post(path, json=payload).json()
    # Force a real FK error after the expense is flushed / old shares deleted.
    with patch('app.services.expenses.split_equally', return_value={uuid4(): 90000}):
        assert api_client.post(path, json=payload).status_code == 409
        assert api_client.patch(path + '/' + original['id'], json={'description': 'Must roll back'}).status_code == 409
    assert api_client.get(path).json() == [original]
    assert api_client.get(base + '/balances').json()['total_amount'] == 90000
