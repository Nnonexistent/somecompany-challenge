import uuid
from typing import AsyncGenerator, Awaitable, Callable, Generator

import pytest
from app import app
from auth import get_password_hash
from conf import BASE_URL
from db.orm import UserOrm
from db.utils import Base, engine, get_db, test_async_session
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


@pytest.fixture()
def api_client() -> AsyncClient:
    return AsyncClient(app=app, base_url=BASE_URL)


@pytest.fixture(
    params=[
        pytest.param(('asyncio', {'use_uvloop': False}), id='asyncio'),
    ],
    scope='session',
    autouse=True,
)
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope='session', autouse=True)
def app_db() -> Generator[None, None, None]:
    async def _test_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_async_session() as session:
            try:
                yield session
            except:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _test_get_db
    yield
    del app.dependency_overrides[get_db]


def _create_all(session: Session) -> None:
    con = session.connection()
    Base.metadata.create_all(con)


def _drop_all(session: Session) -> None:
    con = session.connection()
    Base.metadata.drop_all(con)


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        await session.run_sync(_drop_all)
        await session.run_sync(_create_all)

        yield session

        await session.close()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> UserOrm:
    user = UserOrm(id=uuid.uuid4(), name='user', hashed_password=get_password_hash('qwe123'))
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def get_auth_token(api_client: AsyncClient) -> Callable[[str, str], Awaitable[str]]:
    async def inner(username: str, password: str) -> str:
        async with api_client as client:
            response = await client.post('/auth/token/', data={'username': username, 'password': password})

        assert response.status_code == 200
        return response.json()['access_token']

    return inner
