from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("/", response_model=schemas.Folder)
def create_folder(folder: schemas.FolderCreate, db: Session = Depends(get_db)):
    db_folder = service.create_folder(db, folder)
    return db_folder


@router.get("/{folder_id}", response_model=schemas.Folder)
def read_folder(folder_id: int, db: Session = Depends(get_db)):
    db_folder = service.get_folder(db, folder_id)
    return db_folder


@router.get("/", response_model=list[schemas.Folder])
def read_folders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_folders(db, skip=skip, limit=limit)


@router.patch("/{folder_id}", response_model=schemas.Folder)
def update_folder(
    folder_id: int, folder: schemas.FolderUpdate, db: Session = Depends(get_db)
):
    db_folder = read_folder(folder_id, db)
    updated_device = service.update_folder(db, db_folder, updated_folder=folder)
    return updated_device


@router.delete("/{folder_id}", response_model=schemas.FolderDelete)
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    db_folder = read_folder(folder_id, db)
    deleted_folder_id = service.delete_folder(db, db_folder)
    return {
        "id": deleted_folder_id,
        "msg": f"Folder {deleted_folder_id} removed succesfully!",
    }


@router.get("/{folder_id}/subfolders", response_model=list[schemas.Folder])
def read_subfolders(
    folder_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return service.get_subfolders(
        db, parent_folder_id=folder_id, skip=skip, limit=limit
    )


@router.post("/{folder_id}/subfolders", response_model=schemas.Folder)
def create_subfolder(
    folder_id: int,
    subfolder: schemas.FolderCreate,
    db: Session = Depends(get_db),
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
):
    db_subfolder = read_folder(subfolder_id, db)
    updated_device = service.update_subfolder(
        db, parent_folder_id=folder_id, db_subfolder=db_subfolder, subfolder=subfolder
    )
    return updated_device


@router.delete(
    "/{folder_id}/subfolders/{subfolder_id}", response_model=schemas.FolderDelete
)
def delete_subfolder(folder_id: int, subfolder_id: int, db: Session = Depends(get_db)):
    db_subfolder = read_folder(subfolder_id, db)
    deleted_folder_id = service.delete_subfolder(
        db, parent_folder_id=folder_id, subfolder=db_subfolder
    )
    return {
        "id": deleted_folder_id,
        "msg": f"Subfolder {deleted_folder_id} removed succesfully!",
    }
