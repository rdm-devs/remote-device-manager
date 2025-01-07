import os
import string
import random
import datetime
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from sqlalchemy import delete
from sqlalchemy.orm import Session
from src.auth import models, utils, exceptions
from src.auth.utils import _is_valid_refresh_token
from src.user.models import User

load_dotenv()

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


async def get_refresh_token(
    db: Session,
    refresh_token: str,
) -> Optional[models.AuthRefreshToken]:
    db_refresh_token = (
        db.query(models.AuthRefreshToken)
        .filter(models.AuthRefreshToken.refresh_token == refresh_token)
        .first()
    )
    return db_refresh_token


async def delete_expired_refresh_token(
    db: Session, refresh_token: str
) -> None:
    db.execute(
        delete(models.AuthRefreshToken).where(
            models.AuthRefreshToken.refresh_token == refresh_token
        )
    )
    db.commit()


async def create_refresh_token(
    db: Session,
    user_id: int,
    serial_number: Optional[str] = None,
    db_refresh_token: Optional[models.AuthRefreshToken] = None,
) -> str:
    if db_refresh_token:
        if _is_valid_refresh_token(db_refresh_token):
            return db_refresh_token.refresh_token
        else:
            await delete_expired_refresh_token(db_refresh_token.refresh_token)

    user = db.query(User).filter(User.id == user_id).first()
    expiration_minutes = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")) * 24 * 60
    refresh_token = utils.create_access_token(
        user=user, serial_number=serial_number, expiration_minutes=expiration_minutes
    )

    db_refresh_token = models.AuthRefreshToken(
        user_id=user_id,
        serial_number=serial_number,
        refresh_token=refresh_token,
        expires_at=datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))),
    )
    db.add(db_refresh_token)
    db.commit()
    return refresh_token


async def expire_refresh_token(db: Session, refresh_token: str) -> None:
    db.query(models.AuthRefreshToken).filter(
        models.AuthRefreshToken.refresh_token == refresh_token
    ).update(values={"valid": False, "expires_at": datetime.datetime.now(datetime.UTC)})
    db.commit()


async def get_auth_data_from_token(db: Session, token: str) -> str:
    db_token = await get_refresh_token(db, token)
    if not db_token:
        raise exceptions.InvalidCredentials()
    return db_token.user_id, db_token.serial_number
