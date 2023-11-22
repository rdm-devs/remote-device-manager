from src.schemas import UserWithUserGroups
from sqlalchemy.orm import Session
from . import schemas, models, exceptions
from src.user_group.models import UserGroup


def check_user_exists(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise exceptions.UserNotFoundError()


def check_email_exists(db: Session, email: str, user_id: int | None = None):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user_id and user:
        if user_id != user.id:
            raise exceptions.UserEmailTakenError()
    if user:
        raise exceptions.UserEmailTakenError()


def check_invalid_password(db: Session, password: str):
    valid = len(password.strip()) > 3
    if not valid:
        raise exceptions.UserInvalidPasswordError()


def get_user(db: Session, user_id: int):
    check_user_exists(db, user_id=user_id)
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise exceptions.UserNotFoundError()
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # sanity checks
    check_email_exists(db, email=user.email)
    check_invalid_password(db, password=user.password)

    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session,
    db_user: UserWithUserGroups,
    updated_user: schemas.UserUpdate,
):
    # sanity checks
    values = updated_user.model_dump()
    check_user_exists(db, user_id=db_user.id)
    check_email_exists(db, email=updated_user.email, user_id=db_user.id)
    if updated_user.password:
        check_invalid_password(db, password=updated_user.password)
        values["hashed_password"] = (
            values["password"] + "seriouslyitsnotreallyhashed"
        )  # rehash password

    values.pop("password")

    db.query(models.User).filter(models.User.id == db_user.id).update(values=values)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: UserWithUserGroups):
    # sanity check
    check_user_exists(db, user_id=db_user.id)

    db.delete(db_user)
    db.commit()
    return db_user.id
