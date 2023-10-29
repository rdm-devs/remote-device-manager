from sqlalchemy.orm import Session
from . import schemas, models


def create_tenant(db: Session, tenant: schemas.TenantCreate):
    db_tenant = models.Tenant(**tenant)
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_tenant(db: Session, tenant_id: int):
    return (
        db.query(models.Tenant)
        .filter(models.Tenant.id == tenant_id)
        .first()
    )


def get_tenants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tenant).offset(skip).limit(limit).all()


def get_tenant_by_name(db: Session, tenant_name: str):
    return (
        db.query(models.Tenant)
        .filter(models.Tenant.name == tenant_name)
        .first()
    )


def update_tenant(
    db: Session,
    db_tenant: schemas.Tenant,
    updated_tenant: schemas.TenantUpdate,
):
    db.query(models.Tenant).filter(models.Tenant.id == db_tenant.id).update(
        values=updated_tenant.model_dump()
    )

    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def delete_tenant(db: Session, db_tenant: schemas.Tenant):
    db.delete(db_tenant)
    db.commit()
    return db_tenant.id
