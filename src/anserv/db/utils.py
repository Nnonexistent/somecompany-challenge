import json
from typing import Any, Generator

from conf import SQLALCHEMY_DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def pydantic_friendly_json_serializer(obj: Any) -> str:
    def _pydantic_default(o: Any) -> Any:
        if hasattr(o, 'json') and callable(o.json):
            return o.json()
        return o
    return json.dumps(obj, default=_pydantic_default)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    json_serializer=pydantic_friendly_json_serializer,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
