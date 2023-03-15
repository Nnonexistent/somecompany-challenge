import io
import uuid
from typing import Callable, Generator, Optional

import pytest
from app import app
from auth import get_password_hash
from conf import BASE_URL
from db.orm import UserOrm, EntryOrm
from db.utils import Base, test_engine, test_session
from fastapi.testclient import TestClient
from httpx._auth import Auth
from sqlalchemy.orm import Session
from api.services import parse_uploaded_file
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
def test_user_factory(db_session: Session) -> Callable[..., UserOrm]:
    def inner(name: str = 'user', password: str = 'qwe123') -> UserOrm:
        user = UserOrm(id=uuid.uuid4(), name=name, hashed_password=get_password_hash(password))
        db_session.add(user)
        db_session.commit()
        return user

    return inner


@pytest.fixture
def get_auth(api_client: TestClient) -> Callable[[str, str], TokenAuth]:
    def inner(username: str, password: str) -> TokenAuth:
        with api_client as client:
            response = client.post('/auth/token/', data={'username': username, 'password': password})

        assert response.status_code == 200
        return TokenAuth(response.json()['access_token'])

    return inner


@pytest.fixture
def test_entry_factory(db_session: Session, test_user_factory: Callable[..., UserOrm]) -> Callable[..., EntryOrm]:
    def inner(user: Optional[UserOrm] = None, csv_data: Optional[str] = None) -> EntryOrm:
        if user is None:
            user = test_user_factory()

        if csv_data is None:
            csv_data = (
                'review_time,team,date,merge_time\n'
                '0,Application,2023-01-14,0\n'
                '144299,Application,2023-02-14,1076\n'
                '0,Data Service,2023-01-14,0\n'
                '77,Platform,2023-02-14,102\n'
            )

        fp = io.BytesIO(csv_data.encode())
        entry = parse_uploaded_file(fp, user.id)
        db_session.add(entry)
        db_session.commit()
        return entry

    return inner
