from sqlalchemy.orm import Session
from . import schemas, models


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user_group = (  # checking if user values have a valid user group id
        db.query(models.UserGroup).filter(models.UserGroup.id == user.group_id).first()
    )

    if db_user_group:
        fake_hashed_password = user.password + "notreallyhashed"
        db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    return None


def update_user(
    db: Session,
    db_user: schemas.User,
    updated_user: schemas.UserUpdate,
):
    db_user_group = (  # checking if the updated user values have a valid user group id
        db.query(models.UserGroup)
        .filter(models.UserGroup.id == updated_user.group_id)
        .first()
    )

    if db_user_group:
        db.query(models.User).filter(models.User.id == db_user.id).update(
            values=updated_user.model_dump()
        )
        db.commit()
        db.refresh(db_user)
        return db_user
    return None


def delete_user(db: Session, db_user: schemas.User):
    db.delete(db_user)
    db.commit()
    return db_user.id
