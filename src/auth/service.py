import os
import string
import random
from datetime import datetime, timedelta
from typing import Any
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.auth import models

load_dotenv()

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


async def create_refresh_token(db: Session, user_id: int, refresh_token: str | None = None) -> str:
    if not refresh_token:
        refresh_token = generate_random_alphanum(int(os.getenv("TOKEN_LENGTH")))

    db_refresh_token = models.AuthRefreshToken(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))),
    )
    db.add(db_refresh_token)
    db.commit()
    return refresh_token


async def get_refresh_token(
    db: Session,
    refresh_token: str,
) -> dict[str, Any] | None:
    db_refresh_token = (
        db.query(models.AuthRefreshToken)
        .filter(models.AuthRefreshToken.refresh_token == refresh_token)
        .first()
    )
    return db_refresh_token


async def expire_refresh_token(db: Session, refresh_token_id: int) -> None:
    db.query(models.AuthRefreshToken).filter(
        models.AuthRefreshToken.id == refresh_token_id
    ).update(values={"expires_at": datetime.utcnow() - timedelta(days=1)})
    db.commit()

