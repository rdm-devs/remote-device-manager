from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import List, Optional
from src.exceptions import PermissionDenied
from src.tenant.service import check_tenant_exists
from src.folder.exceptions import (
    FolderNameTakenError,
    FolderNotFoundError,
    InvalidFolderAttrsError,
)
from . import schemas, models
from ..entity.service import create_entity_auto


def check_folder_exist(db: Session, folder_id: int):
    db_folder = db.query(models.Folder).filter(models.Folder.id == folder_id).first()
    if not db_folder:
        raise FolderNotFoundError()


def check_folder_name_taken(db: Session, folder_name: str):
    device_name_taken = (
        db.query(models.Folder).filter(models.Folder.name == folder_name).first()
    )
    if device_name_taken:
        raise FolderNameTakenError()


def create_folder(db: Session, folder: schemas.FolderCreate):
    # sanity check
    check_folder_name_taken(db, folder.name)
    check_tenant_exists(db, folder.tenant_id)

    entity = create_entity_auto(db)
    db_folder = models.Folder(**folder.model_dump(), entity_id=entity.id)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)

    return db_folder


def get_folder(db: Session, folder_id: int):
    db_folder = db.query(models.Folder).filter(models.Folder.id == folder_id).first()
    if db_folder is None:
        raise FolderNotFoundError()
    return db_folder


# def get_folders(db: Session, skip: int = 0, limit: int = 100):
def get_folders(db: Session) -> List[models.Folder]:
    return db.query(models.Folder).filter()  # .all()


def get_folders_from_tenant(db: Session, tenant_id: int) -> List[models.Folder]:
    return db.query(models.Folder).filter(models.Folder.tenant_id == tenant_id) #.all()

def get_folder_by_name(db: Session, folder_name: str):
    folder = db.query(models.Folder).filter(models.Folder.name == folder_name).first()
    if not folder:
        raise FolderNotFoundError()
    return folder


def update_folder(
    db: Session,
    db_folder: schemas.Folder,
    updated_folder: schemas.FolderUpdate,
):
    # sanity checks
    get_folder(db, db_folder.id)
    check_folder_name_taken(db, updated_folder.name)
    if updated_folder.tenant_id:
        check_tenant_exists(db, updated_folder.tenant_id)

    db.query(models.Folder).filter(models.Folder.id == db_folder.id).update(
        values=updated_folder.model_dump(exclude_unset=True)
    )

    db.commit()
    db.refresh(db_folder)
    return db_folder


def delete_folder(db: Session, db_folder: schemas.Folder):
    # sanity check
    check_folder_exist(db, db_folder.id)

    db.delete(db_folder)
    db.commit()
    return db_folder.id


def get_subfolders(db: Session, parent_folder_id: int, skip: int = 0, limit: int = 100):
    # TODO: Test
    # import pdb; pdb.set_trace()
    return (
        db.query(models.Folder.subfolders)
        .where(models.Folder.id == parent_folder_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_subfolder(
    db: Session, parent_folder_id: int, subfolder: schemas.FolderCreate
):
    # sanity check
    parent_folder = get_folder(db, parent_folder_id)
    if not subfolder.parent_id or subfolder.parent_id != parent_folder_id:
        subfolder.parent_id = parent_folder_id
    db_folder = create_folder(db, subfolder)
    return db_folder


def update_subfolder(
    db: Session,
    parent_folder_id: int,
    db_subfolder: schemas.Folder,
    subfolder: schemas.FolderUpdate,
):
    # sanity check
    parent_folder = get_folder(db, parent_folder_id)
    if not subfolder.parent_id or subfolder.parent_id != parent_folder_id:
        raise exceptions.SubfolderParentMismatchError()
    db_folder = update_folder(db, db_subfolder, subfolder)
    return db_folder


def delete_subfolder(db: Session, parent_folder_id: int, subfolder: schemas.Folder):
    # sanity check
    parent_folder = get_folder(db, parent_folder_id)
    if parent_folder.id == subfolder.parent_id:
        db_folder = delete_folder(db, subfolder)
        return db_folder
    else:
        raise exceptions.SubfolderParentMismatchError()
