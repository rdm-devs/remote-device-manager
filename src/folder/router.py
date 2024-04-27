from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from src.auth.dependencies import (
    get_current_active_user,
    has_admin_role,
    has_admin_or_owner_role,
    has_access_to_folder,
    has_access_to_tenant,
    can_edit_folder,
)
from src.user.schemas import User
from src.tenant.router import router as tenant_router
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("/", response_model=schemas.Folder)
def create_folder(
    folder: schemas.FolderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_folder),
):
    db_folder = service.create_folder(db, folder)
    return db_folder


@router.get("/{folder_id}", response_model=schemas.FolderList)
def read_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_folder),
):
    db_folder = service.get_folder(db, folder_id)
    return db_folder


@router.get("/", response_model=Page[schemas.FolderList])
def read_folders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return paginate(service.get_folders(db, user.id))


@tenant_router.get("/{tenant_id}/folders", response_model=Page[schemas.FolderList])
def read_folders(
    tenant_id: Optional[int] = Path(),
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_tenant),
):
    return paginate(service.get_folders_from_tenant(db, tenant_id=tenant_id))


@router.patch("/{folder_id}", response_model=schemas.Folder)
def update_folder(
    folder_id: int,
    folder: schemas.FolderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_folder),
):
    db_folder = read_folder(folder_id, db)
    updated_device = service.update_folder(db, db_folder, updated_folder=folder)
    return updated_device


@router.delete("/{folder_id}", response_model=schemas.FolderDelete)
def delete_folder(
    folder_id: int, db: Session = Depends(get_db), user: User = Depends(can_edit_folder)
):
    db_folder = read_folder(folder_id, db)
    deleted_folder_id = service.delete_folder(db, db_folder)
    return {
        "id": deleted_folder_id,
        "msg": f"Folder {deleted_folder_id} removed succesfully!",
    }


@router.get("/{folder_id}/subfolders", response_model=Page[schemas.FolderList])
def read_subfolders(
    folder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_folder),
):
    return paginate(service.get_subfolders(db, parent_folder_id=folder_id, user_id=user.id))


@router.post("/{folder_id}/subfolders", response_model=schemas.Folder)
def create_subfolder(
    folder_id: int,
    subfolder: schemas.FolderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_folder),
):
    db_folder = service.create_subfolder(
        db, parent_folder_id=folder_id, subfolder=subfolder
    )
    return db_folder


@router.patch("/{folder_id}/subfolders/{subfolder_id}", response_model=schemas.Folder)
def update_subfolder(
    folder_id: int,
    subfolder_id: int,
    subfolder: schemas.FolderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_folder),
):
    db_subfolder = read_folder(subfolder_id, db)
    updated_device = service.update_subfolder(
        db, parent_folder_id=folder_id, db_subfolder=db_subfolder, subfolder=subfolder
    )
    return updated_device


@router.delete(
    "/{folder_id}/subfolders/{subfolder_id}", response_model=schemas.FolderDelete
)
def delete_subfolder(
    folder_id: int,
    subfolder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_folder),
):
    db_subfolder = read_folder(subfolder_id, db)
    deleted_folder_id = service.delete_subfolder(
        db, parent_folder_id=folder_id, subfolder=db_subfolder
    )
    return {
        "id": deleted_folder_id,
        "msg": f"Subfolder {deleted_folder_id} removed succesfully!",
    }
