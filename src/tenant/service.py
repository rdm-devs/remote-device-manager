import os
from dotenv import load_dotenv
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from typing import Union
from src.auth.dependencies import has_access_to_tenant
from src.entity.service import create_entity_auto, update_entity_tags
from src.exceptions import PermissionDenied
from src.tag.models import Tag, Type
from src.tag.service import create_tag
from src.tag.schemas import TagAdminCreate
from src.tenant import schemas, models, exceptions
from src.tenant.utils import (
    check_tenant_exists,
    check_tenant_name_taken,
    filter_tag_ids,
)
from src.folder.service import create_root_folder, delete_folder
from src.folder.schemas import FolderCreate
from src.user.schemas import User
from src.user.models import tenants_and_users_table
from src.user.service import get_user
from pydantic import ValidationError

load_dotenv()


def get_tenant(db: Session, tenant_id: int):
    check_tenant_exists(db, tenant_id)
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()


def get_tenants(db: Session, user_id: int):
    user = get_user(db, user_id)
    tenants = select(models.Tenant).where(models.Tenant.id != 1)
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
    values = tenant.model_dump(exclude_unset=True)
    tags = values.pop("tags", None)

    # creating an Entity for a Tenant
    entity = create_entity_auto(db)
    # creating a Tenant
    db_tenant = models.Tenant(**values, entity_id=entity.id)
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)

    # creating automatic tag
    # TODO: definir una convención de nombres??
    formatted_name = tenant.name.lower().replace(" ", "-")
    db_tenant.add_tag(
        create_tag(
            db,
            TagAdminCreate(
                name=f"tenant-{formatted_name}-tag",
                tenant_id=db_tenant.id,
                type=Type.TENANT,
            ),
        )
    )
    db.commit()
    db.refresh(db_tenant)
    # creating a root folder
    folder = create_root_folder(db, db_tenant.id)

    # assigning tags
    if tags is not None and len(tags) >= 0:
        tag_ids = filter_tag_ids(tags, db_tenant.id)
        tag_ids.extend(
            [t.id for t in db_tenant.tags]
        )  # when creating we want to maintain the automatic tag
        db_tenant.entity = update_entity_tags(
            db=db,
            entity=db_tenant.entity,
            tenant_ids=[db_tenant.id],
            tag_ids=tag_ids,
        )
        db.commit()

    db.refresh(db_tenant)
    create_default_tenant_settings(db, db_tenant.id)
    return db_tenant


def update_tenant(
    db: Session,
    db_tenant: schemas.Tenant,
    updated_tenant: schemas.TenantUpdate,
):
    # sanity checks
    values = updated_tenant.model_dump(exclude_unset=True)
    tags = values.pop("tags", None)

    tenant = get_tenant(db, db_tenant.id)
    check_tenant_name_taken(db, tenant_name=updated_tenant.name, tenant_id=db_tenant.id)

    if tags is not None and len(tags) >= 0:
        tag_ids = filter_tag_ids(tags, tenant.id)
        tenant.entity = update_entity_tags(
            db=db,
            entity=tenant.entity,
            tenant_ids=[tenant.id],
            tag_ids=tag_ids,
        )
        db.commit()

    db.execute(
        update(models.Tenant).where(models.Tenant.id == tenant.id).values(values)
    )
    db.commit()
    db.refresh(tenant)
    return tenant


def delete_tenant(db: Session, db_tenant: schemas.Tenant):
    # sanity check
    if db_tenant.id == 1:
        raise PermissionDenied()
    check_tenant_exists(db, tenant_id=db_tenant.id)
    for folder in db_tenant.folders:
        # deleting only the root folder as children folders will be automatically deleted in cascade
        if folder.parent_id == None:
            delete_folder(db, folder)

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


def get_tenant_settings(db: Session, tenant_id: int):
    check_tenant_exists(db, tenant_id)
    settings = db.scalar(
        select(models.TenantSettings).where(
            models.TenantSettings.tenant_id == tenant_id
        )
    )
    if not settings:
        settings = create_default_tenant_settings(db, tenant_id)
    return settings


def create_default_tenant_settings(db: Session, tenant_id: int):
    return create_tenant_settings(
        db,
        tenant_id,
        schemas.TenantSettingsCreate(heartbeat_s=int(os.getenv("HEARTBEAT_S"))),
    )


def create_tenant_settings(
    db: Session, tenant_id: int, tenant_settings: schemas.TenantSettingsCreate
):
    check_tenant_exists(db, tenant_id)
    settings = models.TenantSettings(
        **tenant_settings.model_dump(exclude_unset=True), tenant_id=tenant_id
    )

    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_tenant_settings(
    db: Session, tenant_id: int, tenant_settings: schemas.TenantSettingsUpdate
):
    check_tenant_exists(db, tenant_id)
    current_settings = get_tenant_settings(db, tenant_id)

    db.execute(
        update(models.TenantSettings)
        .where(models.TenantSettings.tenant_id == tenant_id)
        .values(**tenant_settings.model_dump(exclude_unset=True))
    )
    db.commit()
    db.refresh(current_settings)

    return current_settings
