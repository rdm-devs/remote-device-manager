from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from src.exceptions import BadRequest
from src.auth.utils import get_password_hash
from src.role.service import check_role_exists
from src.role import models as role_models
from src.tenant.models import Tenant, tenants_and_users_table
from src.tenant.utils import check_tenant_exists
from src.folder.models import Folder
from src.device.models import Device
from src.tag.models import Tag
from src.user import schemas, models, exceptions, utils
from src.entity.service import create_entity_auto, update_entity_tags


def check_user_exists(db: Session, user_id: int):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    if not user:
        raise exceptions.UserNotFound()


def check_username_exists(db: Session, username: str, user_id: Optional[int] = None):
    user = db.scalars(
        select(models.User).where(models.User.username == username)
    ).first()
    if user:
        if user_id and user_id != user.id:
            raise exceptions.UsernameTaken()
        if not user_id:
            raise exceptions.UsernameTaken()


def check_invalid_password(db: Session, password: str):
    valid = len(password.strip()) >= 8
    if not valid:
        raise exceptions.UserInvalidPassword()


def get_user(db: Session, user_id: int) -> models.User:
    check_user_exists(db, user_id=user_id)
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    return user


def get_users(db: Session):
    return select(models.User)


def get_folders(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user.is_admin:
        tenant_ids = user.get_tenants_ids()
        return select(Folder).where(Folder.tenant_id.in_(tenant_ids))
    return select(Folder)


def get_devices(db: Session, user_id: int):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    tenant_ids = db.scalars(
        select(tenants_and_users_table.c.tenant_id).where(
            tenants_and_users_table.c.user_id == user_id
        )
    )

    tenant_folder_ids = db.scalars(
        select(Folder.id).where(Folder.tenant_id.in_(tenant_ids))
    )
    devices = select(Device)
    if user.role_id != 1:
        devices = devices.where(
            Device.folder_id.in_(tenant_folder_ids),
        )
    return devices


def create_user(db: Session, user: schemas.UserCreate):
    # sanity checks
    check_username_exists(db, username=user.username)
    check_invalid_password(db, password=user.password)

    default_role = (
        db.query(role_models.Role).filter(role_models.Role.name == "user").first()
    )  # defaul role
    entity = create_entity_auto(db)
    hashed_password = get_password_hash(user.password)

    values = user.model_dump()
    values.pop("password")
    db_user = models.User(
        **values,
        hashed_password=hashed_password,
        entity_id=entity.id,
        role_id=default_role.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_tenants(db: Session, user: models.User, tenant_ids: List[int]):
    tenants = [
        db.scalars(select(Tenant).where(Tenant.id == t_id)).first()
        for t_id in tenant_ids
    ]
    try:
        user.tenants = []
        db.commit()
        user.tenants = tenants
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()


def update_user(
    db: Session,
    db_user: schemas.User,
    updated_user: schemas.UserUpdate,
):
    # sanity checks
    values = updated_user.model_dump(exclude_unset=True)
    tenant_ids = values.pop("tenant_ids", None)
    tags = values.pop("tags", None)

    check_user_exists(db, user_id=db_user.id)
    check_username_exists(db, username=updated_user.username, user_id=db_user.id)

    user = get_user(db, db_user.id)
    if tenant_ids is not None and len(tenant_ids) >= 0:
        user = update_user_tenants(db, user, tenant_ids)
    if tags is not None and len(tags) >= 0:
        user.entity = update_entity_tags(
            db=db,
            entity=user.entity,
            tenant_ids=user.get_tenants_ids(),
            tag_ids=[t["id"] for t in tags],
        )
        db.commit()
    if updated_user.password:
        check_invalid_password(db, password=updated_user.password)
        values["hashed_password"] = get_password_hash(
            values["password"]
        )  # rehash password

        values.pop("password")

    db.execute(update(models.User).where(models.User.id == user.id).values(values))
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, db_user: schemas.User):
    # sanity check
    check_user_exists(db, user_id=db_user.id)

    db.delete(db_user)
    db.commit()
    return db_user.id


def assign_role(db: Session, user_id: int, role_id: int) -> schemas.User:
    check_user_exists(db, user_id)
    check_role_exists(db, role_id)

    user = get_user(db, user_id)
    db.execute(
        update(models.User)
        .where(models.User.id == user.id)
        .values({"role_id": role_id})
    )
    db.commit()
    db.refresh(user)
    return user


def assign_tenant(db: Session, user_id: int, tenant_id: int) -> utils.UserTenant:
    check_user_exists(db, user_id)
    check_tenant_exists(db, tenant_id)
    tenant = db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    user = get_user(db, user_id)

    user.add_tenant(tenant)
    db.commit()
    db.refresh(user)

    return user
