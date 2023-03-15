import json
from typing import Any, AsyncGenerator

from conf import SQLALCHEMY_DATABASE_URL, TEST_SQLALCHEMY_DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def pydantic_friendly_json_serializer(obj: Any) -> str:
    def _pydantic_default(o: Any) -> Any:
        if hasattr(o, 'json') and callable(o.json):
            return o.json()
        return o

    return json.dumps(obj, default=_pydantic_default)


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, json_serializer=pydantic_friendly_json_serializer, future=True)
test_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, json_serializer=pydantic_friendly_json_serializer, future=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
test_async_session = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


# FastAPI Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
