from sqlalchemy import select, insert, update, or_, and_
from sqlalchemy.orm import Session
from typing import Union
from src.auth.dependencies import (
    has_role,
    has_admin_role,
    has_access_to_tenant,
    has_access_to_folder,
    has_access_to_device,
)
from src.user.service import get_user
from src.entity.models import entities_and_tags_table
from src.tenant.models import Tenant, tenants_and_users_table
from src.folder.models import Folder
from src.device.models import Device
from src.tenant.utils import check_tenant_exists
from src.tag import schemas, models, exceptions


def get_tag_by_name(db: Session, tag_name: str):
    tag = db.scalars(
        select(models.Tag).where(models.Tag.name.like(f"%{tag_name}%"))
    ).first()
    if not tag:
        raise exceptions.TagNotFound()
    return tag


def get_tag(db: Session, tag_id: int):
    tag = db.scalars(select(models.Tag).where(models.Tag.id == tag_id)).first()
    if not tag:
        raise exceptions.TagNotFound()
    return tag


def check_tag_name_exists(db: Session, tag_name: str, tenant_id: int):
    # checking if the tag with `tag_name` already exists for tenant with `tenant_id`.
    tag = db.scalars(
        select(models.Tag).where(
            models.Tag.name == tag_name, models.Tag.tenant_id == tenant_id
        )
    ).first()
    if tag:
        raise exceptions.TagNameTaken()


async def get_tags(
    db: Session,
    user_id: int,
    name: Union[str, None] = "",
    tenant_id: Union[int, None] = None,
    folder_id: Union[int, None] = None,
    device_id: Union[int, None] = None,
):

    # if user is not admin, we query only tags created for tenants owned by the current user
    user = get_user(db, user_id)
    tags = select(models.Tag)

    if not user.is_admin:
        tags = (
            tags.join(entities_and_tags_table)
            .where(
                or_(
                    and_(
                        entities_and_tags_table.c.tag_id == models.Tag.id,
                        models.Tag.tenant_id.in_(user.get_tenants_ids()),
                    ),
                    models.Tag.type == models.Type.GLOBAL,
                )
            )
        )

    # testing needed:
    if name:
        tags = tags.where(models.Tag.name.like(f"%{name}%"))
    if tenant_id:
        await has_access_to_tenant(tenant_id, db, user)
        tags = tags.where(
            or_(
                models.Tag.tenant_id == tenant_id, models.Tag.type == models.Type.GLOBAL
            )
        )
    if folder_id:
        await has_access_to_folder(folder_id, db, user)
        folder = db.scalars(select(Folder).where(Folder.id == folder_id)).first()
        folder_tag_ids = [t.id for t in folder.tags]
        tags = tags.where(models.Tag.id.in_(folder_tag_ids))
    if device_id:
        await has_access_to_device(device_id, db, user)
        device = db.scalars(select(Device).where(Device.id == device_id)).first()
        device_tag_ids = [t.id for t in device.tags]
        tags = tags.where(models.Tag.id.in_(device_tag_ids))

    return tags.distinct()


def create_tag(db: Session, tag_schema: schemas.TagAdminCreate):
    if tag_schema.tenant_id:
        check_tenant_exists(db, tenant_id=tag_schema.tenant_id)
    check_tag_name_exists(db, tag_schema.name, tag_schema.tenant_id)

    if tag_schema.type == models.Type.USER_CREATED and tag_schema.tenant_id is None:
        raise exceptions.TagNotFound()
    if tag_schema.type == models.Type.GLOBAL:
        tag_schema.tenant_id = None

    tag = models.Tag(**tag_schema.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, db_tag: schemas.Tag, updated_tag: schemas.TagUpdate):
    get_tag(db, db_tag.id)

    if updated_tag.tenant_id:
        check_tenant_exists(db, updated_tag.tenant_id)
        check_tag_name_exists(
            db, tag_name=updated_tag.name, tenant_id=updated_tag.tenant_id
        )

    res = db.execute(
        update(models.Tag)
        .where(models.Tag.id == db_tag.id)
        .values(updated_tag.model_dump(exclude_unset=True))
    )
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, db_tag: schemas.Tag):
    get_tag(db, db_tag.id)

    db.delete(db_tag)
    db.commit()
    return db_tag.id
