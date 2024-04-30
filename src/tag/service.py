from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Union
from src.auth.dependencies import has_role, has_admin_role
from src.user.schemas import User as UserSchema
from src.user.models import User
from src.user.service import get_user
from src.entity.models import entities_and_tags_table
from src.tenant.models import Tenant, tenants_and_users_table
from src.folder.models import Folder
from src.device.models import Device
from src.tenant.utils import check_tenant_exists
from src.tag import schemas, models, exceptions


def get_tag_by_name(db: Session, tag_name: str):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        raise exceptions.TagNotFound()
    return tag


def get_tag(db: Session, tag_id: int):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise exceptions.TagNotFound()
    return tag


def check_tag_name_exists(db: Session, tag_name: str):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if tag:
        raise exceptions.TagNameTaken()


def get_entity_id(db, model, obj_id):
    # some objects with obj_id may not exist so we return None instead
    # otherwise, the first value in the results tuple is returned
    entity_id = db.query(model.entity_id).filter(model.id == obj_id).first()
    return entity_id[0] if entity_id else None


def get_filters(db, name, tenant_id, folder_id, device_id, user_entity_id):
    entity_ids = []
    folder_entity_id = get_entity_id(db, Folder, folder_id)
    device_entity_id = get_entity_id(db, Device, device_id)
    tenant_entity_id = get_entity_id(db, Tenant, tenant_id)

    entity_ids.extend(
        [folder_entity_id, device_entity_id, tenant_entity_id, user_entity_id]
    )

    # if extra filters are sent, we apply them conditionally
    filters = []
    if entity_ids and any(entity_ids):
        filters.append(models.entities_and_tags_table.columns.entity_id.in_(entity_ids))

    if name:
        name = f"%{name}%"
        filters.append(models.Tag.name.like(name))

    return filters


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
    if user.is_admin:
        return tags

    user_tag_ids = [t.id for t in user.tags]
    tags = (
        tags.join(entities_and_tags_table)
        .where(entities_and_tags_table.c.tag_id == models.Tag.id)
        .where(models.Tag.tenant_id.in_(user.get_tenants_ids()))
    )

    # testing needed:
    if tenant_id:
        tags = tags.where(models.Tag.tenant_id == tenant_id)
    if folder_id:
        folder = db.scalars(select(Folder.id).where(Folder.id == folder_id)).first()
        folder_tag_ids = [t.id for t in folder.tags]
        tags = tags.where(models.Tag.id.in_(folder_tag_ids))
    if device_id:
        device = db.scalars(select(Device).where(Device.id == device_id)).first()
        device_tag_ids = [t.id for t in device.tags]
        tags = tags.where(models.Tag.id.in_(device_tag_ids))

    return tags.distinct()


def create_tag(db: Session, tag: schemas.TagCreate):
    # TODO: definir bien los campos de esta entidad. cuales son obligatorios y/o unicos para chequear restricciones
    check_tag_name_exists(db, tag.name)
    check_tenant_exists(db, tenant_id=tag.tenant_id)

    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def update_tag(db: Session, db_tag: schemas.Tag, updated_tag: schemas.TagUpdate):
    get_tag(db, db_tag.id)

    if updated_tag.tenant_id:
        check_tenant_exists(db, updated_tag.tenant_id)

    db.query(models.Tag).filter(models.Tag.id == db_tag.id).update(
        values=updated_tag.model_dump(exclude_unset=True)
    )
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, db_tag: schemas.Tag):
    get_tag(db, db_tag.id)

    db.delete(db_tag)
    db.commit()
    return db_tag.id
