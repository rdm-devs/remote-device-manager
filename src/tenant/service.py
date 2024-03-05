from sqlalchemy.orm import Session
from typing import Union
from src.auth.dependencies import has_access_to_tenant
from src.tenant.exceptions import TenantNameTakenError, TenantNotFoundError
from src.exceptions import PermissionDenied
from src.tag import service as tags_service
from src.user.schemas import User
from . import schemas, models
from ..entity.service import create_entity_auto


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

    entity = create_entity_auto(db)
    db_tenant = models.Tenant(**tenant.model_dump(), entity_id=entity.id)
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


async def get_tenant_tags(
    db: Session,
    user: User,
    name: Union[str, None] = "",
    tenant_id: Union[int, None] = None,
    folder_id: Union[int, None] = None,
    device_id: Union[int, None] = None,
):
    check_tenant_exists(db, tenant_id)
    if await has_access_to_tenant(tenant_id, db, user):
        return tags_service.get_tags(
            db,
            user,
            tenant_id=tenant_id,
            folder_id=folder_id,
            device_id=device_id,
            name=name,
        )
    else:
        raise PermissionDenied()
