from sqlalchemy.orm import Session
from . import schemas, models
from src.tenant.exceptions import TenantNameTakenError, TenantNotFoundError


def check_tenant_exists(db: Session, tenant_id: int):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise TenantNotFoundError()


def check_tenant_name_taken(db: Session, tenant_name: str):
    tenant = db.query(models.Tenant).filter(models.Tenant.name == tenant_name).first()
    if tenant:
        raise TenantNameTakenError()


def get_tenant(db: Session, tenant_id: int):
    check_tenant_exists(db, tenant_id)
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()


def get_tenants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tenant).offset(skip).limit(limit).all()


def get_tenant_by_name(db: Session, tenant_name: str):
    db_tenant = (
        db.query(models.Tenant).filter(models.Tenant.name == tenant_name).first()
    )
    if not db_tenant:
        raise TenantNotFoundError()
    return db_tenant


def create_tenant(db: Session, tenant: schemas.TenantCreate):
    check_tenant_name_taken(db, tenant.name)

    db_tenant = models.Tenant(**tenant.model_dump())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def update_tenant(
    db: Session,
    db_tenant: schemas.Tenant,
    updated_tenant: schemas.TenantUpdate,
):
    # sanity checks
    check_tenant_exists(db, db_tenant.id)
    check_tenant_name_taken(db, updated_tenant.name)

    db.query(models.Tenant).filter(models.Tenant.id == db_tenant.id).update(
        values=updated_tenant.model_dump()
    )

    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def delete_tenant(db: Session, db_tenant: schemas.Tenant):
    # sanity check
    check_tenant_exists(db, tenant_id=db_tenant.id)

    db.delete(db_tenant)
    db.commit()
    return db_tenant.id
