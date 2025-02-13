import os
import string
import random
import datetime
from hashlib import sha256
from jose import JWTError, jwt
from typing import Any, Dict, Optional, Union
from dotenv import load_dotenv
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from src.auth import models, utils, exceptions, schemas, constants
from src.auth.utils import (
    _is_valid_refresh_token,
    get_user_by_username,
    get_most_recent_valid_recovery_token,
    expire_invalid_recovery_tokens,
    expire_used_recovery_token,
)
from src.user.models import User
from src.user.service import update_user
from src.user.schemas import UserUpdate

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


async def delete_refresh_token(db: Session, refresh_token: str) -> None:
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
) -> str:
    if not serial_number:
        db_refresh_token = db.scalar(
            select(models.AuthRefreshToken).where(
                models.AuthRefreshToken.user_id == user_id
            )
        )
    else:
        db_refresh_token = db.scalars(
            select(models.AuthRefreshToken).where(
                models.AuthRefreshToken.serial_number == serial_number
            )
        ).first()

    if db_refresh_token:
        if _is_valid_refresh_token(db_refresh_token):
            return db_refresh_token.refresh_token
        else:
            await delete_refresh_token(db, db_refresh_token.refresh_token)

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


def create_recovery_token(db: Session, user: User) -> models.AuthPasswordRecoveryToken:
    # Expiring invalid tokens first
    expire_invalid_recovery_tokens(db, user.username)

    # Checking and retrieving existing valid recovery token
    existing_recovery_token = get_most_recent_valid_recovery_token(db, user.username)
    if existing_recovery_token:
        return existing_recovery_token

    # Creating a new recovery token if none exists
    expiration_date = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=int(os.getenv("RECOVERY_TOKEN_EXPIRATION_MINUTES"))
    )

    new_key = sha256(user.hashed_password[-10:].encode("utf-8")).hexdigest()
    recovery_token = jwt.encode(
        {"user_id": user.id, "email": user.username, "exp": expiration_date},
        new_key,
        algorithm=os.getenv("ALGORITHM"),
    )

    db_recovery_token = models.AuthPasswordRecoveryToken(
        email=user.username, recovery_token=recovery_token, expires_at=expiration_date
    )

    db.add(db_recovery_token)
    db.commit()
    db.refresh(db_recovery_token)

    return db_recovery_token


def send_password_recovery_email(
    db: Session, forgot_password_data: schemas.ForgotPasswordData
) -> schemas.ForgotPasswordEmailSent:
    user = get_user_by_username(db, forgot_password_data.email)
    recovery_token_obj = create_recovery_token(db, user)
    recovery_url = f"{os.getenv('MAIN_SITE_DOMAIN_PROD')}/password-recovery/?token={recovery_token_obj.recovery_token}"
    # TODO: send a real email with a message containing the recovery URL.
    print(recovery_token_obj.recovery_token)

    message = constants.Message.EMAIL_SENT_MSG.substitute({"email": user.username})
    return schemas.ForgotPasswordEmailSent(msg=message, url=recovery_url)


def update_user_password(
    db: Session, password_update_data: schemas.PasswordUpdateData
) -> User:
    user = get_user_by_username(db, password_update_data.email)
    new_user = update_user(
        db, user, UserUpdate(password=password_update_data.new_password)
    )
    db.execute(
        delete(models.AuthPasswordRecoveryToken).where(
            models.AuthPasswordRecoveryToken.email == password_update_data.email
        )
    )
    db.commit()
    return new_user
