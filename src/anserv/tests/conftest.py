import typing
import uuid
from typing import Callable, Generator

import pytest
from app import app
from auth import get_password_hash
from conf import BASE_URL
from db.orm import UserOrm
from db.utils import Base, test_engine, test_session
from fastapi.testclient import TestClient
from httpx._auth import Auth
from sqlalchemy.orm import Session

from httpx._models import Request, Response


class TokenAuth(Auth):
    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers['Authorization'] = f'Bearer {self.token}'
        yield request


@pytest.fixture()
def api_client() -> TestClient:
    return TestClient(app=app, base_url=BASE_URL)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    with test_session() as session:
        yield session

        session.close()


@pytest.fixture
def test_user(db_session: Session) -> UserOrm:
    user = UserOrm(id=uuid.uuid4(), name='user', hashed_password=get_password_hash('qwe123'))
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def get_auth(api_client: TestClient) -> Callable[[str, str], TokenAuth]:
    def inner(username: str, password: str) -> TokenAuth:
        with api_client as client:
            response = client.post('/auth/token/', data={'username': username, 'password': password})

        assert response.status_code == 200
        return TokenAuth(response.json()['access_token'])

    return inner
