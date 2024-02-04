from sqlalchemy.orm import Session
from . import schemas, models


def get_tag_by_name(db: Session, tag_name: str):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        raise TagNotFoundError()
    return tag


def get_tag(db: Session, tag_id: int):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise TagNotFoundError()
    return tag


def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tag).offset(skip).limit(limit).all()


def create_tag(db: Session, tag: schemas.TagCreate):
    # TODO: definir bien los campos de esta entidad. cuales son obligatorios y/o unicos para chequear restricciones
    # check_tag_exist(db, tag.tag_group_id)

    db_tag = models.tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def update_tag(db: Session, db_tag: schemas.Tag, updated_tag: schemas.TagUpdate):
    get_tag(db, db_tag.id)

    db.query(models.tag).filter(models.tag.id == db_tag.id).update(
        values=updated_tag.model_dump()
    )
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, db_tag: schemas.Tag):
    get_tag(db, db_tag.id)

    db.delete(db_tag)
    db.commit()
    return db_tag.id
