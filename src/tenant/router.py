from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.auth.dependencies import get_current_active_user
from src.user.schemas import User
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/", response_model=schemas.Tenant)
def create_tenant(
    tenant: schemas.TenantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_tenant = service.create_tenant(db, tenant)
    return db_tenant


@router.get("/{tenant_id}", response_model=schemas.Tenant)
def read_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_tenant = service.get_tenant(db, tenant_id=tenant_id)
    return db_tenant


@router.get("/", response_model=List[schemas.Tenant])
def read_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    return service.get_tenants(db, skip=skip, limit=limit)


@router.patch("/{tenant_id}", response_model=schemas.Tenant)
def update_tenant(
    tenant_id: int,
    tenant: schemas.TenantUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_tenant = read_tenant(tenant_id, db)
    updated_tenant = service.update_tenant(db, db_tenant, updated_tenant=tenant)
    return updated_tenant


@router.delete("/{tenant_id}", response_model=schemas.TenantDelete)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_tenant = read_tenant(tenant_id, db)
    deleted_tenant_id = service.delete_tenant(db, db_tenant)
    return {
        "id": deleted_tenant_id,
        "msg": f"Tenant {deleted_tenant_id} removed succesfully!",
    }
