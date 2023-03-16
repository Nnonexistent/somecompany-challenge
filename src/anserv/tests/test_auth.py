from typing import Any, Callable

import pytest
from db.orm import UserOrm
from fastapi.testclient import TestClient

from .conftest import TokenAuth


def test_auth(api_client: TestClient, user_factory: Callable[..., UserOrm]) -> None:
    password = 'qwe'
    user = user_factory('user', password)

    with api_client as client:
        response = client.post('/auth/token/', data={'username': user.name, 'password': password})

    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'


def test_auth_negative(api_client: TestClient, user_factory: Callable[..., UserOrm]) -> None:
    user = user_factory()
    with api_client as client:
        response = client.post('/auth/token/', data={'username': user.name, 'password': 'invalid'})

    assert response.status_code == 401


@pytest.mark.parametrize(
    'username, password',
    [
        ('qwe', 'asd'),
        ('', ''),
        (None, ''),
        ('', None),
    ],
)
def test_auth_negative_no_user(api_client: TestClient, username: Any, password: Any) -> None:
    with api_client as client:
        response = client.post('/auth/token/', data={'username': username, 'password': password})

    assert response.status_code // 100 == 4  # don't care about specific code as long as it's 4xx


def test_entries_listing_access(
    api_client: TestClient, get_auth: Callable[[str, str], TokenAuth], user_factory: Callable[..., UserOrm]
) -> None:
    user = user_factory()

    with api_client as client:
        response = client.get('/entries/', auth=get_auth(user.name, 'qwe123'))

    assert response.status_code == 200


def test_entries_listing_no_auth(api_client: TestClient) -> None:
    with api_client as client:
        response = client.get('/entries/')

    assert response.status_code == 401


def test_entries_listing_invalid_token(api_client: TestClient, user_factory: Callable[..., UserOrm]) -> None:
    user_factory()
    with api_client as client:
        response = client.get('/entries/', auth=TokenAuth('qwe'))

    assert response.status_code == 401
