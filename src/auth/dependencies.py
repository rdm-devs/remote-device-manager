import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from src.database import get_db
from src.user.schemas import User
from .schemas import TokenData
from .exceptions import InactiveUserError, InvalidCredentialsError
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
