from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.entity import schemas, models, exceptions
from src.tag.models import Tag
from typing import List


def create_entity_auto(db: Session):
    return create_entity(db, schemas.EntityCreate())


def create_entity(db: Session, entity: schemas.EntityCreate):
    db_entity = models.Entity(**entity.model_dump())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def delete_entity(db: Session, entity_id: int):
    get_entity(db, entity_id)

    db.delete(entity_id)
    db.commit()
    return entity_id


def update_entity_tags(
    db: Session, entity: models.Entity, tenant_ids: List[int], tag_ids: List[int]
) -> models.Entity:
    # in order to update the entity's tags, we must ensure we have access to the tenants
    # for which the tags were created. That is why we receive tenant_ids.
    if not tenant_ids:
        raise exceptions.EntityTenantRelationshipMissing()

    tag_ids = list(set(tag_ids)) # filtering duplicated tag_ids
    tags = db.scalars(
        select(Tag).where(Tag.id.in_(tag_ids), Tag.tenant_id.in_(tenant_ids))
    ).all()

    try:
        entity.tags = []
        db.commit()
        entity.tags = tags
        db.commit()
        db.refresh(entity)
        return entity
    except IntegrityError:
        db.rollback()
