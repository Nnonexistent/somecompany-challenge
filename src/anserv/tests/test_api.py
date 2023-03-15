from typing import Callable

from db.orm import UserOrm
from fastapi.testclient import TestClient

from .conftest import TokenAuth


def test_root(api_client: TestClient) -> None:
    with api_client as client:
        response = client.get('/')

    assert response.status_code == 200


def test_auth(api_client: TestClient, test_user: UserOrm) -> None:
    with api_client as client:
        response = client.post('/auth/token/', data={'username': test_user.name, 'password': 'qwe123'})

    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'


def test_entries_listing(
    api_client: TestClient, get_auth: Callable[[str, str], TokenAuth], test_user: UserOrm
) -> None:
    with api_client as client:
        response = client.get('/entries/', auth=get_auth(test_user.name, 'qwe123'))

    assert response.status_code == 200
