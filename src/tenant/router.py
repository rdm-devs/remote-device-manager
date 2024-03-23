from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from src.auth.dependencies import (
    get_current_active_user,
    has_admin_or_owner_role,
    has_access_to_tenant,
)
from src.user.schemas import User
from src.tag import schemas as tags_schemas
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/", response_model=schemas.Tenant)
def create_tenant(
    tenant: schemas.TenantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    db_tenant = service.create_tenant(db, tenant)
    return db_tenant


@router.get("/{tenant_id}", response_model=schemas.Tenant)
def read_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_tenant),
):
    db_tenant = service.get_tenant(db, tenant_id=tenant_id)
    return db_tenant


@router.get("/", response_model=List[schemas.Tenant])
def read_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    return service.get_tenants(db, skip=skip, limit=limit)


@router.patch("/{tenant_id}", response_model=schemas.Tenant)
def update_tenant(
    tenant_id: int,
    tenant: schemas.TenantUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_tenant),
):
    db_tenant = read_tenant(tenant_id, db)
    updated_tenant = service.update_tenant(db, db_tenant, updated_tenant=tenant)
    return updated_tenant


@router.delete("/{tenant_id}", response_model=schemas.TenantDelete)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_tenant),
):
    db_tenant = read_tenant(tenant_id, db)
    deleted_tenant_id = service.delete_tenant(db, db_tenant)
    return {
        "id": deleted_tenant_id,
        "msg": f"Tenant {deleted_tenant_id} removed succesfully!",
    }


@router.get("/{tenant_id}/tags", response_model=Page[tags_schemas.Tag])
async def read_tags(
    tenant_id: int,
    folder_id: Union[int, None] = None,
    device_id: Union[int, None] = None,
    name: Union[str, None] = None,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_tenant),
):

    return paginate(
        await service.get_tenant_tags(
            db,
            user,
            tenant_id=tenant_id,
            folder_id=folder_id,
            device_id=device_id,
            name=name,
        )
    )
