from sqlalchemy import select, update, or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.entity import schemas, models, exceptions
from src.tag.models import Tag, Type, entities_and_tags_table
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
