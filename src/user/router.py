from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import List
from src.auth.dependencies import (
    get_current_active_user,
    has_admin_role,
    has_admin_or_owner_role,
)
from src.tenant.schemas import TenantList
from src.device.schemas import DeviceList
from src.folder.schemas import Folder
from . import service, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=Page[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_role),
):
    users = service.get_users(db)
    return paginate(db, users)


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_role),
):
    db_user = service.get_user(db, user_id=user_id)
    return db_user


@router.patch("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(has_admin_role),
):
    db_user = read_user(user_id, db)
    updated_user = service.update_user(db, db_user, updated_user=user)
    return updated_user


@router.delete("/{user_id}", response_model=schemas.UserDelete)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_role),
):
    db_user = read_user(user_id, db)
    deleted_user_user_id = service.delete_user(db, db_user)
    if not deleted_user_user_id:
        raise HTTPException(status_code=400, detail="User could not be deleted")
    return {
        "id": deleted_user_user_id,
        "msg": f"User {deleted_user_user_id} removed succesfully!",
    }


@router.patch("/{user_id}/role", response_model=schemas.UserRole)
def assign_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_role),
):
    service.assign_role(db=db, user_id=user_id, role_id=role_id)
    return schemas.UserRole(id=user_id, role_id=role_id)


@router.get("/{user_id}/tenants", response_model=Page[TenantList])
async def read_tenants(
    user_id: str = Path(),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    if user_id == "me":
        user_id = user.id
    tenants = service.get_tenants(db, user_id=int(user_id))
    return paginate(db, tenants)


@router.get("/{user_id}/devices", response_model=Page[DeviceList])
async def read_devices(
    user_id: str = Path(),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    if user_id == "me":
        user_id = user.id
    devices = service.get_devices(db, user_id=int(user_id))
    return paginate(db, devices)


@router.get("/{user_id}/folders", response_model=Page[Folder])
async def read_folders(
    user_id: str = Path(),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    if user_id == "me":
        user_id = user.id
    folders = service.get_folders(db, user_id=int(user_id))
    return paginate(db, folders)
