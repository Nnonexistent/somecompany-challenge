import datetime
from typing import Any, Dict, Literal, Optional, Union

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from conf import AUTH_ALGORITHM, AUTH_SECRET_KEY, AUTH_TOKEN_EXPIRE_MINUTES
from db.orm import UserOrm
from db.utils import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token/')
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl='auth/token/', auto_error=False)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Token(BaseModel):
    access_token: str
    token_type: Literal['bearer']


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserOrm]:
    res = await db.execute(select(UserOrm).filter(UserOrm.name == username))
    try:
        user = res.one()[0]
    except NoResultFound:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    assert isinstance(user, UserOrm)
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Union[datetime.timedelta, None] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=AUTH_ALGORITHM)
    return encoded_jwt


async def get_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserOrm:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    res = await db.execute(select(UserOrm).where(UserOrm.name == username))
    try:
        user = res.one()[0]
    except NoResultFound:
        raise credentials_exception
    assert isinstance(user, UserOrm)
    return user


async def get_user_or_none(
    db: AsyncSession = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[UserOrm]:
    if not token:
        return None

    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        username = payload.get('sub')
        if username is None:
            return None
    except JWTError:
        return None

    res = await db.execute(select(UserOrm).where(UserOrm.name == username))
    try:
        user = res.one()[0]
    except NoResultFound:
        return None
    assert isinstance(user, UserOrm)
    return user


async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = datetime.timedelta(minutes=AUTH_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({'sub': user.name}, access_token_expires)
    return Token(access_token=access_token, token_type='bearer')
