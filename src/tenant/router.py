from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter()


@router.post("/tenants/", response_model=schemas.Tenant)
def create_tenant(tenant: schemas.TenantCreate, db: Session = Depends(get_db)):
    db_tenant = service.get_tenant_by_name(db, tenant_name=tenant.name)
    if db_tenant:
        raise HTTPException(status_code=400, detail="Tenant name already registered")
    return db_tenant


@router.get("/tenants/{tenant_id}", response_model=schemas.Tenant)
def read_tenant(tenant_id: int, db: Session = Depends(get_db)):
    db_tenant = service.get_tenant(db, tenant_id=tenant_id)
    if db_tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return db_tenant


@router.get("/tenants/", response_model=list[schemas.Tenant])
def read_tenants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_tenants(db, skip=skip, limit=limit)


@router.patch("/tenants/{tenant_id}", response_model=schemas.Tenant)
def update_tenant(
    tenant_id: int, tenant: schemas.TenantUpdate, db: Session = Depends(get_db)
):
    db_tenant = read_tenant(tenant_id, db)
    updated_tenant = service.update_tenant(db, db_tenant, updated_tenant=tenant)
    if not updated_tenant:
        raise HTTPException(status_code=400, detail="Tenant could not be updated")
    return updated_tenant


@router.delete("/tenants/{tenant_id}", response_model=schemas.TenantDelete)
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    db_tenant = read_tenant(tenant_id, db)
    deleted_tenant_id = service.delete_tenant(db, db_tenant)
    if not deleted_tenant_id:
        raise HTTPException(status_code=400, detail="Tenant could not be deleted")
    return {
        "id": deleted_tenant_id,
        "msg": f"tenant group {deleted_tenant_id} removed succesfully!",
    }
