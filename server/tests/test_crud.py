from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import Session

from app.config import Settings
from app.db.session import get_session
from app.main import create_app
from app.models import Group, Member


def create_group(client, name="Viaje"):
    response = client.post("/api/groups", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_groups_crud(api_client):
    assert api_client.get("/api/groups").json() == []
    group = create_group(api_client, "  Viaje  ")
    path = f"/api/groups/{group['id']}"
    assert group["name"] == "Viaje"
    assert set(group) == {"id", "name", "created_at"}
    assert api_client.get(path).json() == group
    assert api_client.get("/api/groups").json() == [group]
    response = api_client.patch(path, json={"name": " Casa "})
    assert response.status_code == 200
    assert response.json() == {**group, "name": "Casa"}
    response = api_client.delete(path)
    assert response.status_code == 204 and response.content == b""
    assert api_client.get(path).status_code == 404
    assert api_client.get("/api/groups").json() == []


def test_members_crud_and_group_deletion(api_client):
    group = create_group(api_client)
    group_path = f"/api/groups/{group['id']}"
    path = f"{group_path}/members"
    assert api_client.get(path).json() == []
    response = api_client.post(path, json={"name": " Ana "})
    assert response.status_code == 201
    member = response.json()
    assert member["name"] == "Ana" and member["group_id"] == group["id"]
    assert set(member) == {"id", "name", "created_at", "group_id"}
    assert api_client.get(path).json() == [member]
    response = api_client.delete(group_path)
    assert response.status_code == 409
    assert api_client.get(group_path).status_code == 200
    assert api_client.get(path).json() == [member]
    member_path = f"{path}/{member['id']}"
    response = api_client.patch(member_path, json={"name": " Andrea "})
    assert response.status_code == 200
    assert response.json() == {**member, "name": "Andrea"}
    response = api_client.delete(member_path)
    assert response.status_code == 204 and response.content == b""
    assert api_client.get(path).json() == []
    assert api_client.delete(member_path).status_code == 404
    assert api_client.delete(group_path).status_code == 204


def test_member_must_belong_to_group(api_client):
    first = create_group(api_client)
    second = create_group(api_client, "Casa")
    first_path = f"/api/groups/{first['id']}/members"
    second_path = f"/api/groups/{second['id']}/members"
    member = api_client.post(first_path, json={"name": "Ana"}).json()
    assert api_client.get(second_path).json() == []
    path = f"{second_path}/{member['id']}"
    assert api_client.patch(path, json={"name": "Cambio"}).status_code == 404
    assert api_client.delete(path).status_code == 404
    assert api_client.get(first_path).json() == [member]


@pytest.mark.parametrize("payload", [{}, {"name": ""}, {"name": " \t\n"}, {"name": None}, {"name": 123}, {"name": "Ana", "group_id": str(uuid4())}])
def test_invalid_names_for_create_and_update(api_client, payload):
    group = create_group(api_client)
    group_path = f"/api/groups/{group['id']}"
    members_path = f"{group_path}/members"
    member = api_client.post(members_path, json={"name": "Ana"}).json()
    for method, path in [
        ("post", "/api/groups"), ("patch", group_path),
        ("post", members_path), ("patch", f"{members_path}/{member['id']}"),
    ]:
        assert getattr(api_client, method)(path, json=payload).status_code == 422
    assert api_client.get(group_path).json() == group
    assert api_client.get(members_path).json() == [member]


@pytest.mark.parametrize("method,suffix,payload", [
    ("get", "", None), ("patch", "", {"name": "Nuevo"}), ("delete", "", None),
    ("get", "/members", None), ("post", "/members", {"name": "Ana"}),
    ("patch", f"/members/{uuid4()}", {"name": "Ana"}),
    ("delete", f"/members/{uuid4()}", None),
])
def test_missing_group(api_client, method, suffix, payload):
    assert api_client.request(method, f"/api/groups/{uuid4()}{suffix}", json=payload).status_code == 404


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_missing_member(api_client, method):
    group = create_group(api_client)
    path = f"/api/groups/{group['id']}/members/{uuid4()}"
    assert api_client.request(method, path, json={"name": "Ana"} if method == "patch" else None).status_code == 404


@pytest.mark.parametrize("method,suffix,payload", [
    ("get", "", None), ("patch", "", {"name": "Viaje"}), ("delete", "", None),
    ("get", "/members", None), ("post", "/members", {"name": "Ana"}),
    ("patch", f"/members/{uuid4()}", {"name": "Ana"}),
    ("delete", f"/members/{uuid4()}", None),
])
def test_invalid_group_uuid(api_client, method, suffix, payload):
    assert api_client.request(method, f"/api/groups/invalid{suffix}", json=payload).status_code == 422


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_invalid_member_uuid(api_client, method):
    group = create_group(api_client)
    path = f"/api/groups/{group['id']}/members/invalid"
    assert api_client.request(method, path, json={"name": "Ana"} if method == "patch" else None).status_code == 422


def test_database_enforces_foreign_key(postgres_engine):
    with postgres_engine.connect() as connection:
        transaction = connection.begin()
        try:
            with Session(connection, join_transaction_mode="create_savepoint") as session:
                session.add(Member(group_id=uuid4(), name="Huérfano"))
                with pytest.raises(IntegrityError):
                    session.commit()
                session.rollback()
                group = Group(name="FK")
                session.add(group)
                session.commit()
                session.refresh(group)
                session.add(Member(group_id=group.id, name="Ana"))
                session.commit()
                session.delete(group)
                with pytest.raises(IntegrityError):
                    session.commit()
                session.rollback()
        finally:
            transaction.rollback()


def test_commit_is_visible_from_independent_connection(postgres_engine):
    application = create_app(Settings())

    def override_session():
        with Session(postgres_engine) as session:
            yield session

    application.dependency_overrides[get_session] = override_session
    with TestClient(application) as client:
        group = create_group(client, "Persistencia")
        with Session(postgres_engine) as other_session:
            assert other_session.get(Group, group["id"]).name == "Persistencia"
        assert client.delete(f"/api/groups/{group['id']}").status_code == 204


def test_database_errors_are_sanitized():
    application = create_app(Settings())

    def broken_session():
        raise OperationalError("SELECT private_data", {}, Exception("private-password"))
        yield

    application.dependency_overrides[get_session] = broken_session
    with TestClient(application) as client:
        response = client.get("/api/groups")
        assert response.status_code == 500
        assert "private" not in response.text
