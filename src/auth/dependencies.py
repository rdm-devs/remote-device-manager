import os
from dotenv import load_dotenv
from datetime import datetime
from fastapi import Depends, FastAPI, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Any, Dict
from src.exceptions import PermissionDenied
from src.database import get_db
from src.user.schemas import User
from src.user import service as user_service
from src.role import models as role_models
from src.tenant import models as tenant_models
from src.folder import models as folder_models
from src.device import models as device_models
from src.tag import models as tag_models
from src.auth import service, exceptions
from src.auth.schemas import TokenData
from src.auth.utils import get_user_by_username

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
        user_str = payload.get("sub")
        if user_str is None:
            raise exceptions.InvalidCredentials()
        user = User.model_validate_json(
            user_str
        )  # creating User schema with the data from the token.
        token_data = TokenData(username=user.username)
    except JWTError:
        raise exceptions.InvalidCredentials()
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise exceptions.InvalidCredentials()
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise exceptions.InactiveUser()
    return current_user


async def has_role(
    role_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> User:
    role = db.query(role_models.Role).filter(role_models.Role.name == role_name).first()
    if role and user.role_id == role.id:
        return user
    return None


async def has_admin_role(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> User:
    user = await has_role("admin", db, user)
    if user:
        return user
    raise PermissionDenied()


async def has_owner_role(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> User:
    user = await has_role("owner", db, user)
    if user:
        return user
    raise PermissionDenied()


async def has_admin_or_owner_role(
    db: Session = Depends(get_db), user: User = Depends(get_current_active_user)
) -> User:
    admin_user = await has_role("admin", db, user)
    owner_user = await has_role("owner", db, user)
    if admin_user or owner_user:
        return user
    raise PermissionDenied()


async def valid_refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    db_refresh_token = await service.get_refresh_token(db, refresh_token)
    if not db_refresh_token:
        raise exceptions.RefreshTokenNotValid()

    if not _is_valid_refresh_token(db_refresh_token):
        raise exceptions.RefreshTokenNotValid()

    return db_refresh_token


async def valid_refresh_token_user(
    refresh_token: Dict[str, Any] = Depends(valid_refresh_token),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    user = user_service.get_user(db, refresh_token.user_id)
    if not user:
        raise exceptions.RefreshTokenNotValid()

    return user


def _is_valid_refresh_token(db_refresh_token: Dict[str, Any]) -> bool:
    return datetime.utcnow() <= db_refresh_token.expires_at


async def has_access_to_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    if await has_role("admin", db, user):
        return user
    else:  # owner or user role verification
        count = (
            db.query(tenant_models.tenants_and_users_table)
            .filter(
                tenant_models.tenants_and_users_table.c.tenant_id == tenant_id,
                tenant_models.tenants_and_users_table.c.user_id == user.id,
            )
            .count()
        )
        if count == 1:
            return user

    raise PermissionDenied()


async def has_access_to_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    folder = (
        db.query(folder_models.Folder)
        .filter(folder_models.Folder.id == folder_id)
        .first()
    )

    if folder and (await has_access_to_tenant(folder.tenant_id, db, user)):
        return user


async def has_access_to_tag(
    tag_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    tags = (
        db.query(tag_models.Tag)
        .filter(tag_models.Tag.name.like(f"%{tag_name}%"))
        .filter(await has_access_to_tenant(tag_models.Tag.tenant_id, db, user))
        .all()
    )

    if tags:
        return user


async def has_access_to_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    device = (
        db.query(device_models.Device)
        .filter(device_models.Device.id == device_id)
        .first()
    )

    if device and (await has_access_to_folder(device.folder_id, db, user)):
        return user


async def can_edit_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    return await has_access_to_device(device_id, db, user)


async def can_edit_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    return await has_access_to_folder(folder_id, db, user)
