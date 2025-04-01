from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Optional
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
from src.database import get_db
from src.folder import service, schemas
from src.utils import CustomBigPage

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("/", response_model=schemas.Folder)
def create_folder(
    folder: schemas.FolderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    db_folder = service.create_folder(db, folder)
    return db_folder


@router.get("/{folder_id}", response_model=schemas.Folder)
def read_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_folder),
):
    db_folder = service.get_folder(db, folder_id)
    return db_folder


@router.get("/", response_model=CustomBigPage[schemas.Folder])
def read_folders(
    tenant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return paginate(db, service.get_folders_from_tenant(db, user.id, tenant_id))


@tenant_router.get("/{tenant_id}/folders", response_model=CustomBigPage[schemas.Folder])
def read_folders_from_tenant(
    tenant_id: int = Path(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return read_folders(tenant_id, db, user)


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
        "msg": f"Carpeta {deleted_folder_id} eliminada exitosamente!",
    }


# @router.get("/{folder_id}/subfolders", response_model=CustomBigPage[schemas.Folder])
# def read_subfolders(
#     folder_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(has_access_to_folder),
# ):
#     return paginate(
#         service.get_subfolders(db, parent_folder_id=folder_id, user_id=user.id)
#     )


# @router.post("/{folder_id}/subfolders", response_model=schemas.Folder)
# def create_subfolder(
#     folder_id: int,
#     subfolder: schemas.FolderCreate,
#     db: Session = Depends(get_db),
#     user: User = Depends(can_edit_folder),
# ):
#     db_folder = service.create_subfolder(
#         db, parent_folder_id=folder_id, subfolder=subfolder
#     )
#     return db_folder


# @router.patch("/{folder_id}/subfolders/{subfolder_id}", response_model=schemas.Folder)
# def update_subfolder(
#     folder_id: int,
#     subfolder_id: int,
#     subfolder: schemas.FolderUpdate,
#     db: Session = Depends(get_db),
#     user: User = Depends(can_edit_folder),
# ):
#     db_subfolder = read_folder(subfolder_id, db)
#     updated_device = service.update_subfolder(
#         db, parent_folder_id=folder_id, db_subfolder=db_subfolder, subfolder=subfolder
#     )
#     return updated_device


# @router.delete(
#     "/{folder_id}/subfolders/{subfolder_id}", response_model=schemas.FolderDelete
# )
# def delete_subfolder(
#     folder_id: int,
#     subfolder_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(can_edit_folder),
# ):
#     db_subfolder = read_folder(subfolder_id, db)
#     deleted_folder_id = service.delete_subfolder(
#         db, parent_folder_id=folder_id, subfolder=db_subfolder
#     )
#     return {
#         "id": deleted_folder_id,
#         "msg": f"Subfolder {deleted_folder_id} removed succesfully!",
#     }
