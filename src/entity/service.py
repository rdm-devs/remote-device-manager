from sqlalchemy import select, update, delete, or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.entity import schemas, models, exceptions
from src.tag.models import Tag, Type, entities_and_tags_table
from typing import List


def get_entity(db: Session, entity_id: int) -> models.Entity:
    entity = db.scalars(select(models.Entity).where(models.Entity.id == entity_id)).first()
    if not entity:
        raise exceptions.EntityNotFound()
    return entity

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

    # gathering new tags if they are global type or belong to a valid tenant_id
    new_tags_query = select(Tag).where(
        Tag.id.in_(tag_ids),
        or_(
            Tag.type == Type.GLOBAL,
            Tag.tenant_id.in_(tenant_ids),
        ),
    )
    new_tags = db.scalars(new_tags_query).all()

    try:
        entity.tags = []
        db.commit()
        entity.tags = list(set(new_tags))
        db.commit()
        db.refresh(entity)
        return entity
    except IntegrityError:
        db.rollback()


def get_entity_tag_ids(db: Session, entity_id: int):
    entity_tag_ids = db.scalars(
        select(entities_and_tags_table.c.tag_id).where(
            entities_and_tags_table.c.entity_id == entity_id,
        )
    ).all()
    return entity_tag_ids


def delete_entity_tags(
    db: Session, entity: models.Entity, tag_ids: List[int]
) -> models.Entity:

    # gathering tags
    deleted_tags_query = delete(Tag).where(
        Tag.id.in_(tag_ids)
    )

    try:
        entity.tags = []
        db.commit()
        db.execute(deleted_tags_query)
        db.commit()
        db.refresh(entity)
        return entity
    except IntegrityError:
        db.rollback()
