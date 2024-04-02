from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Union, List
from src.auth.dependencies import (
    get_current_active_user,
    has_admin_role,
    has_admin_or_owner_role,
    has_access_to_tag,
)
from src.user.schemas import User
from src.user.router import router as user_router
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=schemas.Tag)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_tag = service.create_tag(db, tag)
    return db_tag


@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_tag = service.get_tag(db, tag_id)
    return db_tag


@user_router.get("/{user_id}/tags", response_model=Page[schemas.Tag])
@router.get("/", response_model=Page[schemas.Tag])
async def read_tags(
    user_id: Union[int, str, None] = None,
    tenant_id: Union[int, None] = None,
    folder_id: Union[int, None] = None,
    device_id: Union[int, None] = None,
    name: Union[str, None] = None,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    if not user_id or user_id == "me":
        user_id = user.id
    return paginate(
        await service.get_tags(
            db,
            tenant_id=tenant_id,
            folder_id=folder_id,
            device_id=device_id,
            user_id=user_id,
            name=name,
        )
    )


@router.patch("/{tag_id}", response_model=schemas.Tag)
def update_tag(
    tag_id: int,
    tag: schemas.TagUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_tag = read_tag(tag_id, db)
    updated_device = service.update_tag(db, db_tag, updated_tag=tag)
    if not updated_device:
        raise HTTPException(status_code=400, detail="Tag could not be updated")
    return updated_device


@router.delete("/{tag_id}", response_model=schemas.TagDelete)
def delete_device(
    tag_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_tag_group = read_tag(tag_id, db)
    deleted_tag_id = service.delete_tag(db, db_tag_group)
    if not deleted_tag_id:
        raise HTTPException(status_code=400, detail="Tag could not be deleted")
    return {
        "id": deleted_tag_id,
        "msg": f"Tag {deleted_tag_id} removed succesfully!",
    }
