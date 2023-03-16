import json
from typing import Any, AsyncGenerator

from conf import SQLALCHEMY_URL, TEST_SQLALCHEMY_URL, SQLALCHEMY_USE_NULLPOOL
from pydantic.json import pydantic_encoder
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool


def pydantic_json_serializer(obj: Any) -> str:
    return json.dumps(obj, default=pydantic_encoder)


poolclass = NullPool if SQLALCHEMY_USE_NULLPOOL else None

async_engine = create_async_engine(SQLALCHEMY_URL, json_serializer=pydantic_json_serializer, poolclass=poolclass)
test_engine = create_engine(TEST_SQLALCHEMY_URL, json_serializer=pydantic_json_serializer)

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore
test_session = sessionmaker(test_engine, expire_on_commit=False)


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
