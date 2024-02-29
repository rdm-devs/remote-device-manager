import os
from dotenv import load_dotenv
from datetime import datetime
from fastapi import Depends, FastAPI, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Any, Dict
from src.database import get_db
from src.user.schemas import User
from src.user import service as user_service
from src.auth import service
from .schemas import TokenData
from .exceptions import InactiveUserError, InvalidCredentialsError, RefreshTokenNotValid
from .utils import get_user_by_username

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = payload.get("sub")
        if username is None:
            raise InvalidCredentialsError()
        token_data = TokenData(username=username)
    except JWTError:
        raise InvalidCredentialsError()
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise InvalidCredentialsError()
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise InactiveUserError()
    return current_user


async def valid_refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    db_refresh_token = await service.get_refresh_token(db, refresh_token)
    if not db_refresh_token:
        raise RefreshTokenNotValid()

    if not _is_valid_refresh_token(db_refresh_token):
        raise RefreshTokenNotValid()

    return db_refresh_token


async def valid_refresh_token_user(
    refresh_token: Dict[str, Any] = Depends(valid_refresh_token),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    user = user_service.get_user(db, refresh_token.user_id)
    if not user:
        raise RefreshTokenNotValid()

    return user


def _is_valid_refresh_token(db_refresh_token: Dict[str, Any]) -> bool:
    return datetime.utcnow() <= db_refresh_token.expires_at
