import os
import datetime
import pyotp
import ssl
import smtplib
from fastapi import Depends
from hashlib import sha256
from pydantic import EmailStr
from dotenv import load_dotenv
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import Session
from typing import Any, Optional, Dict, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.database import get_db
from src.user import models as user_models
from src.user import schemas as user_schemas
from src.user import exceptions as user_exceptions
from src.auth import exceptions
from src.auth.models import AuthPasswordRecoveryToken as RecoveryToken
from src.auth import schemas as auth_schemas
from src.device.models import Device
from src.device import exceptions as device_exceptions

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_username(db: Session, username: str) -> user_models.User:
    user = db.scalars(
        select(user_models.User).where(user_models.User.username == username)
    ).first()
    if not user:
        raise user_exceptions.UserNotFound()
    return user


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not verify_password(password, user.hashed_password):
        raise exceptions.IncorrectUserOrPassword()
    return user


def encode_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt


def create_access_token(
    user: user_models.User,
    serial_number: Optional[str] = None,
    expiration_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
):
    serialized_user = user_schemas.User.model_validate(user).model_dump_json()
    access_token_expires = datetime.timedelta(minutes=expiration_minutes)
    access_token = encode_access_token(
        data={"sub": serialized_user, "sn": serial_number},
        expires_delta=access_token_expires,
    )
    return access_token


def get_refresh_token_settings(
    refresh_token: str,
    expired: bool = False,
) -> Dict[str, Any]:
    base_cookie = {
        "key": os.getenv("REFRESH_SECRET_KEY"),
        "httponly": True,
        "samesite": "none",
        "secure": os.getenv("SECURE_COOKIES"),
        "domain": os.getenv(f"API_SITE_DOMAIN_{os.getenv("ENV")}"),
    }
    if expired:
        return base_cookie

    return {
        **base_cookie,
        "value": refresh_token,
        "max_age": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")),
    }


def check_device_has_rustdesk_credentials(db: Session, device_id: Union[str, int]):
    device = db.scalars(
        select(Device).where(
            or_(Device.id == device_id, Device.serial_number == device_id)
        )
    ).first()
    if not device:
        raise device_exceptions.DeviceNotFound()
    if not device.id_rust or not device.pass_rust:
        raise device_exceptions.DeviceCredentialsNotConfigured()
    return device


def is_valid_otp(otp: str) -> bool:
    totp = pyotp.TOTP(
        os.getenv("SECRET_OTP_KEY"), interval=int(os.getenv("OTP_INTERVAL_SECS"))
    )
    if totp.verify(otp):
        return otp
    raise exceptions.InvalidOTP()


def create_connection_url(db: Session, device_id: Union[str, int], otp: str):
    _ = check_device_has_rustdesk_credentials(db, device_id)

    base_url = os.getenv(f"RUSTDESK_CLIENT_URL")
    return f"{base_url}?id={device_id}&otp={otp}"


def create_otp(interval: int = int(os.getenv("OTP_INTERVAL_SECS"))):
    # should I write this in the db here?
    totp = pyotp.TOTP(os.getenv("SECRET_OTP_KEY"), interval=interval)
    return totp.now()


def create_connection_token(
    db: Session,
    device_id: Union[str, int],
    expiration_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
) -> str:
    device = check_device_has_rustdesk_credentials(db, device_id)

    serialized_conn_token = auth_schemas.ConnectionToken.model_validate(
        device
    ).model_dump_json()
    conn_token_expires = datetime.timedelta(minutes=expiration_minutes)
    conn_token = encode_access_token(
        data={"sub": serialized_conn_token}, expires_delta=conn_token_expires
    )
    return conn_token


def _is_valid_refresh_token(db_refresh_token: auth_schemas.AuthRefreshToken) -> bool:
    return datetime.datetime.now(
        datetime.UTC
    ) <= db_refresh_token.expires_at.astimezone(datetime.UTC)


def get_most_recent_valid_recovery_token(
    db: Session, email: str
) -> Union[RecoveryToken, None]:
    return db.scalar(
        select(RecoveryToken)
        .where(
            RecoveryToken.email == email,
            RecoveryToken.expires_at > datetime.datetime.now(datetime.UTC),
        )
        .order_by(RecoveryToken.expires_at.desc())
    )


def expire_invalid_recovery_tokens(db: Session, email: str):
    db.execute(
        delete(RecoveryToken).where(
            RecoveryToken.email == email,
            RecoveryToken.expires_at < datetime.datetime.now(datetime.UTC),
        )
    )
    db.commit()


def expire_used_recovery_token(db: Session, email: str):
    db.execute(delete(RecoveryToken).where(RecoveryToken.email == email))
    db.commit()


def get_user_password_update_token(
    token: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        recovery_token_obj = db.scalar(
            select(RecoveryToken).where(RecoveryToken.recovery_token == token)
        )
        if not recovery_token_obj:
            raise exceptions.InvalidPasswordUpdateToken()

        user = get_user_by_username(db, username=payload.get("email"))
        if (
            payload.get("email") != recovery_token_obj.email
            or payload.get("user_id") != user.id
        ):
            raise exceptions.InvalidPasswordUpdateToken()
        return user
    except JWTError:
        raise exceptions.InvalidPasswordUpdateToken()


def send_email(receiver_email: str, message: str):
    port = os.getenv("SMTP_PORT")  # For starttls
    smtp_server = os.getenv("SMTP_SERVER")
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.encode("utf-8"))
