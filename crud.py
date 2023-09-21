from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserGroup).offset(skip).limit(limit).all()

def get_user_group_by_name(db: Session, name: str):
    return db.query(models.UserGroup).filter(models.UserGroup.name == name).first()

def create_user_group(db: Session, user_group: schemas.UserGroupCreate):
    db_user_group = models.UserGroup(name=user_group.name)
    db.add(db_user_group)
    db.commit()
    db.refresh(db_user_group)
    return db_user_group

def update_user_group(db: Session, user_group: schemas.UserGroupUpdate):
    db_user_group = db.query(models.UserGroup) \
                        .update() \
                        .where(models.UserGroup.id == user_group.id) \
                        .values(**user_group)
    db.commit()
    db.refresh(db_user_group)
    return db_user_group



# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item