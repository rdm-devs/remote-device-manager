from sqlalchemy.orm import Session
from src.exceptions import PermissionDenied
from . import schemas, models, exceptions
from src.user.models import User


def check_role_name_taken(db: Session, role_name: str):
    role_name_taken = (
        db.query(models.Role).filter(models.Role.name == role_name).first()
    )
    if role_name_taken is not None:
        raise exceptions.RoleNameTaken()

def check_role_exists(db: Session, role_id: int):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise exceptions.RoleNotFound()

def get_role(db: Session, role_id: int):
    check_role_exists(db, role_id=role_id)
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    role = db.query(models.Role).filter(models.Role.name == name).first()
    if not role:
        raise exceptions.RoleNotFound()
    return role


def get_roles(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user.is_admin:
        return db.query(models.Role)
    else:
        return db.query(models.Role).filter(models.Role.id > user.role_id)


def create_role(db: Session, role: schemas.RoleCreate):
    # sanity checks
    check_role_name_taken(db, role.name)

    db_role = models.Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(
    db: Session, db_role: schemas.Role, updated_role: schemas.RoleUpdate
):
    # sanity checks
    check_role_exists(db, db_role.id)
    check_role_name_taken(db, updated_role.name)

    db.query(models.Role).filter(models.Role.id == db_role.id).update(
        values=updated_role.model_dump()
    )
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, db_role: schemas.Role):
    # sanity check
    check_role_exists(db, role_id=db_role.id)

    db.delete(db_role)
    db.commit()
    return db_role.id
