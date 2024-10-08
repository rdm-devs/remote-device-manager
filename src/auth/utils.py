import os
import datetime
import pyotp
from fastapi import Depends
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Any, Optional, Dict, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.database import get_db
from src.user import models, schemas
from src.user import exceptions as user_exceptions
from src.auth import exceptions
from src.auth import schemas as auth_schemas
from src.device.models import Device
from src.device import exceptions as device_exceptions

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_username(db: Session, username: str) -> models.User:
    user = db.scalars(
        select(models.User).where(models.User.username == username)
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
    user: models.User,
    expiration_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
):
    serialized_user = schemas.User.model_validate(user).model_dump_json()
    access_token_expires = datetime.timedelta(minutes=expiration_minutes)
    access_token = encode_access_token(
        data={"sub": serialized_user}, expires_delta=access_token_expires
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

def check_device_has_rustdesk_credentials(db: Session, device_id: int):
    device = db.scalars(select(Device).where(Device.id == device_id)).first()
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

def create_connection_url(db: Session, device_id: int, otp: str):
    _ = check_device_has_rustdesk_credentials(db, device_id)

    base_url = os.getenv(f"RUSTDESK_CLIENT_URL")
    return f"{base_url}?id={device_id}&otp={otp}"

def create_otp(interval: int = int(os.getenv("OTP_INTERVAL_SECS"))):
    # should I write this in the db here?
    totp = pyotp.TOTP(os.getenv("SECRET_OTP_KEY"), interval=interval)
    return totp.now()


def create_connection_token(
    db: Session,
    device_id: int,
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
