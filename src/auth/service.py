import os
import string
import random
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.auth import models, utils
from src.user.models import User

load_dotenv()

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


async def create_refresh_token(
    db: Session, user_id: int, refresh_token: Optional[models.AuthRefreshToken] = None
) -> str:

    if refresh_token:
        await expire_refresh_token(db, refresh_token=refresh_token.refresh_token)
    user = db.query(User).filter(User.id == user_id).first()
    expiration_minutes = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")) * 24 * 60
    refresh_token = utils.create_access_token(
        user=user, expiration_minutes=expiration_minutes
    )

    db_refresh_token = models.AuthRefreshToken(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow()
        + timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))),
    )
    db.add(db_refresh_token)
    db.commit()
    return refresh_token


async def get_refresh_token(
    db: Session,
    refresh_token: str,
) -> Optional[Dict[str, Any]]:
    db_refresh_token = (
        db.query(models.AuthRefreshToken)
        .filter(models.AuthRefreshToken.refresh_token == refresh_token)
        .first()
    )
    return db_refresh_token


async def expire_refresh_token(db: Session, refresh_token: str) -> None:
    db.query(models.AuthRefreshToken).filter(
        models.AuthRefreshToken.refresh_token == refresh_token
    ).update(values={"valid": False, "expires_at": datetime.utcnow()})
    db.commit()
