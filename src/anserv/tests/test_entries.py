import io
from typing import Any, Callable, Dict

import pytest
from db.orm import UserOrm, EntryOrm
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from .conftest import TokenAuth
from sqlalchemy import select
from .csv_samples import VALID_SAMPLES, INVALID_SAMPLES


def test_entries_listing(
    api_client: TestClient, get_auth: Callable[[str, str], TokenAuth], test_entry_factory: Callable[..., EntryOrm]
) -> None:
    test_entry_factory()
    with api_client as client:
        response = client.get('/entries/', auth=get_auth('user', 'qwe123'))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_entries_listing_other_user(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    test_entry_factory: Callable[..., EntryOrm],
    test_user_factory: Callable[..., UserOrm],
) -> None:
    test_entry_factory()
    user = test_user_factory('other', 'qwe123')

    with api_client as client:
        response = client.get('/entries/', auth=get_auth(user.name, 'qwe123'))

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_entries_detail(
    api_client: TestClient, get_auth: Callable[[str, str], TokenAuth], test_entry_factory: Callable[..., EntryOrm]
) -> None:
    entry = test_entry_factory()
    with api_client as client:
        response = client.get(f'/entries/{entry.id}/', auth=get_auth('user', 'qwe123'))

    assert response.status_code == 200
    assert response.json()['id'] == str(entry.id)


def test_entries_remove(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    test_entry_factory: Callable[..., EntryOrm],
    db_session: Session,
) -> None:
    entry = test_entry_factory()
    with api_client as client:
        response = client.delete(f'/entries/{entry.id}/', auth=get_auth('user', 'qwe123'))

    assert response.status_code // 100 == 2

    assert not db_session.query(select(EntryOrm).exists()).scalar()


@pytest.mark.parametrize('csv_data, expected_stats', VALID_SAMPLES)
def test_entry_create(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    test_user_factory: Callable[..., UserOrm],
    csv_data: str,
    expected_stats: Dict[str, Any],
    db_session: Session,
) -> None:
    user = test_user_factory()

    files = {'payload': io.BytesIO(csv_data.encode())}
    with api_client as client:
        response = client.post('/entries/', auth=get_auth(user.name, 'qwe123'), files=files)

    assert response.status_code == 201

    obj_dict = response.json()
    for name, value in expected_stats.items():
        assert obj_dict[name] == value

    assert db_session.query(select(EntryOrm).exists()).scalar()


@pytest.mark.parametrize('csv_data', INVALID_SAMPLES)
def test_entry_create(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    test_user_factory: Callable[..., UserOrm],
    csv_data: str,
) -> None:
    user = test_user_factory()

    files = {'payload': io.BytesIO(csv_data.encode())}
    with api_client as client:
        response = client.post('/entries/', auth=get_auth(user.name, 'qwe123'), files=files)

    assert response.status_code == 422
