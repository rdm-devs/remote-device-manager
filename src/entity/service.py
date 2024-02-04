from sqlalchemy.orm import Session
from . import schemas, models


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
