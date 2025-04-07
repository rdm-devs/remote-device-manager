from sqlalchemy import Select, select, insert, update, or_, and_, delete, func
from sqlalchemy.orm import Session
from typing import Union, List, Optional
from src.auth.dependencies import (
    has_role,
    has_admin_role,
    has_access_to_tenant,
    has_access_to_folder,
    has_access_to_device,
)
from src.user.service import get_user
from src.user.models import User
from src.entity.models import entities_and_tags_table
from src.entity.service import get_entity_tag_ids
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


def check_tag_name_exists(db: Session, tag_name: str, tenant_id: int, tag_id: Optional[int] = None):
    # checking if the tag with `tag_name` already exists for tenant with `tenant_id`.
    tag = db.scalars(
        select(models.Tag).where(
            func.lower(models.Tag.name) == tag_name.lower(),
            models.Tag.tenant_id == tenant_id,
        )
    ).first()
    if tag:
        if tag_id and tag_id != tag.id:
            raise exceptions.TagNameTaken()
        if not tag_id:
            raise exceptions.TagNameTaken()


async def get_tags(
    db: Session,
    auth_user: User,
    user_id: int,
    name: Union[str, None] = "",
    tenant_id: Union[int, None] = None,
    folder_id: Union[int, None] = None,
    device_id: Union[int, None] = None,
    ignore_user_id: bool = True,
):

    # if user is not admin, we query only tags created for tenants owned by the current user
    user = get_user(db, user_id)
    tags = select(models.Tag)
    tag_ids = []

    if not user.is_admin:
        user_assigned_tag_ids = get_entity_tag_ids(db, user.entity_id)
        tag_ids = user_assigned_tag_ids

    # testing needed:
    if tenant_id:
        await has_access_to_tenant(tenant_id, db, auth_user)
        tenant = db.scalars(select(Tenant).where(Tenant.id == tenant_id)).first()
        tenant_assigned_tag_ids = get_entity_tag_ids(db, tenant.entity_id)
        tag_ids = tenant_assigned_tag_ids

    if folder_id:
        await has_access_to_folder(folder_id, db, auth_user)
        folder = db.scalars(select(Folder).where(Folder.id == folder_id)).first()
        folder_assigned_tag_ids = get_entity_tag_ids(db, folder.entity_id)
        tag_ids = folder_assigned_tag_ids

    if device_id:
        await has_access_to_device(device_id, db, auth_user)
        device = db.scalars(select(Device).where(Device.id == device_id)).first()
        device_assigned_tag_ids = get_entity_tag_ids(db, device.entity_id)
        tag_ids = device_assigned_tag_ids

    if tag_ids:
        tags = tags.where(models.Tag.id.in_(tag_ids))

    if name:
        tags = tags.where(models.Tag.name.like(f"%{name}%"))

    assigned_tags = db.scalars(tags.distinct()).all()

    return assigned_tags


def get_tenant_available_tags(db: Session, tenant_id: int, tags: Select):
    return tags.where(
        or_(
            models.Tag.tenant_id == tenant_id,
            models.Tag.type == models.Type.GLOBAL,
        )
    )


def get_folder_available_tags(db: Session, folder_id: int, tags: Select):
    folder = db.scalars(select(Folder).where(Folder.id == folder_id)).first()
    auto_folder_tag_id = (
        select(entities_and_tags_table.c.tag_id)
        .join(models.Tag)
        .join(
            Folder,
            onclause=Folder.tenant_id == folder.tenant_id,
        )
        .where(
            or_(
                models.Tag.type == models.Type.TENANT,
                models.Tag.type == models.Type.FOLDER,
                models.Tag.type == models.Type.USER_CREATED,
            ),
            or_(
                entities_and_tags_table.c.entity_id == folder.entity_id,
                entities_and_tags_table.c.entity_id == folder.tenant.entity_id,
            ),
        )
    )
    return tags.where(
        or_(
            models.Tag.type == models.Type.GLOBAL,
            models.Tag.id.in_(auto_folder_tag_id),
        ),
    )


def get_device_available_tags(db: Session, device_id: int, tags: Select):
    device = db.scalars(select(Device).where(Device.id == device_id)).first()
    auto_device_tag_id = (
        select(models.Tag.id)
        .join(
            entities_and_tags_table,
            onclause=or_(
                # including device and device's folder tags
                entities_and_tags_table.c.entity_id == device.entity_id,
                entities_and_tags_table.c.entity_id == device.folder.entity_id,
                entities_and_tags_table.c.entity_id == device.folder.tenant.entity_id,
            ),
        )
        .where(
            or_(
                models.Tag.type == models.Type.DEVICE,
                models.Tag.type == models.Type.FOLDER,
                models.Tag.type == models.Type.TENANT,
                models.Tag.type == models.Type.USER_CREATED,
            ),
            models.Tag.tenant_id == device.folder.tenant_id,
            entities_and_tags_table.c.tag_id == models.Tag.id,
        )
    )

    return tags.where(
        or_(
            models.Tag.type == models.Type.GLOBAL,
            models.Tag.id.in_(auto_device_tag_id),
        )
    )


async def get_available_tags(
    db: Session,
    auth_user: User,
    user_id: int,
    name: Union[str, None] = "",
    tenant_id: Union[int, None] = None,
    folder_id: Union[int, None] = None,
    device_id: Union[int, None] = None,
    ignore_user_id: bool = True,
):

    user = get_user(db, user_id)
    tags = select(models.Tag)
    if not user.is_admin:
        tags = tags.where(
            or_(
                models.Tag.tenant_id.in_(user.get_tenants_ids()),
                models.Tag.type == models.Type.GLOBAL,
            )
        )

    if tenant_id:
        await has_access_to_tenant(tenant_id, db, auth_user)
        tags = get_tenant_available_tags(db, tenant_id, tags)

    if folder_id:
        await has_access_to_folder(folder_id, db, auth_user)
        tags = get_folder_available_tags(db, folder_id, tags)

    if device_id:
        await has_access_to_device(device_id, db, auth_user)
        tags = get_device_available_tags(db, device_id, tags)

    if name:
        tags = tags.where(models.Tag.name.like(f"%{name}%"))

    available_tags = db.scalars(tags.distinct()).all()
    return available_tags


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
        db, tag_name=updated_tag.name, tenant_id=updated_tag.tenant_id, tag_id=db_tag.id
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


def delete_tag_multi(db: Session, user: User, tag_ids: List[int]) -> List[int]:
    result = db.execute(
        delete(models.Tag).where(
            models.Tag.id.in_(tag_ids),
            models.Tag.type == models.Type.USER_CREATED,
            or_(models.Tag.created_by_id == user.id, user.is_admin),
            models.Tag.tenant_id != 1,
        )
    )
    db.commit()
    return tag_ids, result.rowcount
