from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import List
from src.auth.dependencies import (
    get_current_active_user,
    has_admin_role,
    has_admin_or_owner_role,
    has_access_to_tenant,
    has_access_to_user,
    can_assign_role
)
from src.database import get_db
from src.device.schemas import DeviceList
from src.folder.schemas import Folder
from src.tenant.service import get_tenants
from src.tenant.schemas import Tenant
from src.utils import CustomBigPage
from src.user import service, schemas, utils, exceptions

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=CustomBigPage[utils.UserTenant])
def read_users(
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    users = service.get_users(db, user)
    return paginate(db, users)


@router.get("/{user_id}", response_model=utils.UserTenant)
def read_user(
    user_id: int = Depends(has_access_to_user),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    db_user = service.get_user(db, user_id=user_id)
    return db_user


@router.post("/", response_model=utils.UserTenant)
async def create_user(
    user: schemas.UserCreateFull,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(has_admin_or_owner_role),
):
    if not await can_assign_role(user.role_id, db, auth_user):
        raise exceptions.PermissionDenied()
    return service.create_user_full(db, user)

@router.patch("/{user_id}", response_model=utils.UserTenant)
def update_user(
    user: schemas.UserUpdate,
    user_id: int = Depends(has_access_to_user),
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(has_admin_or_owner_role),
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
    if user_id == user.id:
        raise exceptions.UserCannotDeleteItself()
    db_user = read_user(user_id, db)
    deleted_user_user_id = service.delete_user(db, db_user)
    if not deleted_user_user_id:
        raise HTTPException(status_code=400, detail="El usuario no pudo ser eliminado")
    return {
        "id": deleted_user_user_id,
        "msg": f"Usuario {deleted_user_user_id} eliminado exitosamente!",
    }


@router.patch("/{user_id}/role", response_model=schemas.User)
def assign_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_role),
):
    return service.assign_role(db=db, user_id=user_id, role_id=role_id)


@router.patch("/{user_id}/tenant", response_model=utils.UserTenant)
def assign_tenant(
    user_id: int,
    tenant_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    user = service.assign_tenant(db=db, user_id=user_id, tenant_id=tenant_id)
    return user


@router.get("/{user_id}/tenants", response_model=CustomBigPage[Tenant])
async def read_tenants(
    user_id: str = Path(),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    if user_id == "me":
        user_id = user.id
    tenants = get_tenants(db, user_id=int(user_id))
    return paginate(db, tenants)


@router.get("/{user_id}/devices", response_model=CustomBigPage[DeviceList])
async def read_devices(
    user_id: str = Path(),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    if user_id == "me":
        user_id = user.id
    devices = service.get_devices(db, user_id=int(user_id))
    return paginate(db, devices)


@router.get("/{user_id}/folders", response_model=CustomBigPage[Folder])
async def read_folders(
    user_id: str = Path(),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(has_admin_or_owner_role),
):
    if user_id == "me":
        user_id = user.id
    folders = service.get_folders(db, user_id=int(user_id))
    return paginate(db, folders)
