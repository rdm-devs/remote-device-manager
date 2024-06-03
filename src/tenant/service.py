from sqlalchemy import select, update
from sqlalchemy.orm import Session
from typing import Union
from src.auth.dependencies import has_access_to_tenant
from src.entity.service import create_entity_auto, update_entity_tags
from src.exceptions import PermissionDenied
from src.tag.models import Tag
from src.tag.service import create_tag
from src.tag.schemas import TagCreate
from src.tenant import schemas, models, exceptions
from src.tenant.utils import (
    check_tenant_exists,
    check_tenant_name_taken,
    filter_tag_ids,
)
from src.folder.service import create_root_folder
from src.folder.schemas import FolderCreate
from src.user.schemas import User
from src.user.models import tenants_and_users_table
from src.user.service import get_user


def get_tenant(db: Session, tenant_id: int):
    check_tenant_exists(db, tenant_id)
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()


def get_tenants(db: Session, user_id: int):
    user = get_user(db, user_id)
    tenants = select(models.Tenant)
    if user.is_admin:
        return tenants
    else:
        tenant_ids = user.get_tenants_ids()
        return tenants.where(models.Tenant.id.in_(tenant_ids))


def get_tenant_by_name(db: Session, tenant_name: str):
    db_tenant = (
        db.query(models.Tenant).filter(models.Tenant.name == tenant_name).first()
    )
    if not db_tenant:
        raise exceptions.TenantNotFound()
    return db_tenant


def create_tenant(db: Session, tenant: schemas.TenantCreate):
    check_tenant_name_taken(db, tenant_name=tenant.name)

    entity = create_entity_auto(db)
    db_tenant = models.Tenant(**tenant.model_dump(), entity_id=entity.id)
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)

    # TODO: definir una convención de nombres??
    formatted_name = tenant.name.lower().replace(" ", "-")
    tenant_tag = create_tag(
        db, TagCreate(name=f"tenant-{formatted_name}-tag", tenant_id=db_tenant.id)
    )
    folder = create_root_folder(db, db_tenant.id)

    return db_tenant


def update_tenant(
    db: Session,
    db_tenant: schemas.Tenant,
    updated_tenant: schemas.TenantUpdate,
):
    # sanity checks
    values = updated_tenant.model_dump(exclude_unset=True)
    #check_tenant_exists(db, db_tenant.id)
    tenant = get_tenant(db, db_tenant.id)
    check_tenant_name_taken(db, tenant_name=updated_tenant.name, tenant_id=db_tenant.id)

    if updated_tenant.tags:
        tags = values.pop("tags")
        tag_ids = filter_tag_ids(tags, tenant.id)
        tenant.entity = update_entity_tags(
            db=db,
            entity=tenant.entity,
            tenant_ids=[tenant.id],
            tag_ids=tag_ids,
        )

    db.execute(
        update(models.Tenant).where(models.Tenant.id == tenant.id).values(values)
    )
    db.commit()
    db.refresh(tenant)
    return tenant


def delete_tenant(db: Session, db_tenant: schemas.Tenant):
    # sanity check
    check_tenant_exists(db, tenant_id=db_tenant.id)
    if len(db_tenant.folders) > 0:
        raise exceptions.TenantCannotBeDeleted()

    db.delete(db_tenant)
    db.commit()
    return db_tenant.id


async def get_tenant_tags(
    db: Session,
    user: User,
    tenant_id: Union[int, None] = None,
):
    check_tenant_exists(db, tenant_id)
    if await has_access_to_tenant(tenant_id, db, user):
        return (
            select(Tag)
            .join(models.Tenant)
            .where(models.Tenant.id == tenant_id)
            .where(Tag.tenant_id == tenant_id)
        )
    else:
        raise PermissionDenied()
