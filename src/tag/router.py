from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

# from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from src.utils import CustomBigPage
from typing import Union, List, Dict, Any
from src.auth.dependencies import (
    get_current_active_user,
    has_admin_role,
    has_admin_or_owner_role,
    has_access_to_tags,
    has_access_to_user,
    has_access_to_user_id,
)
from src.user.schemas import User
from src.user.router import router as user_router
from src.database import get_db
from src.tag import service, schemas
from src.exceptions import PermissionDenied

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=schemas.Tag)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    #print(f"auth_user_ctx.get(): {auth_user_ctx.get()}")
    db_tag = service.create_tag(db, tag)
    return db_tag


@user_router.get("/{user_id}/tags", response_model=schemas.AvailableAssignedTags)
@router.get("/", response_model=schemas.AvailableAssignedTags)
async def read_tags(
    user_id: Union[int, str, None] = None,
    tenant_id: Union[int, None] = None,
    folder_id: Union[int, None] = None,
    device_id: Union[int, None] = None,
    name: Union[str, None] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    if tenant_id == 1 and user.role_id != 1:
        raise PermissionDenied()
    if not user_id or user_id == "me":
        ignore_user_id = True
        user_id = user.id
    else:
        ignore_user_id = False

    await has_access_to_user_id(user_id, db, user)
    available_tags = await service.get_available_tags(
        db, user, user_id, name, tenant_id, folder_id, device_id, ignore_user_id
    )
    assigned_tags = await service.get_tags(
        db, user, user_id, name, tenant_id, folder_id, device_id, ignore_user_id
    )
    return schemas.AvailableAssignedTags(available=available_tags, assigned=assigned_tags)


@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_tag = service.get_tag(db, tag_id)
    if db_tag.tenant_id == 1 and user.role_id != 1:
        raise PermissionDenied()
    return db_tag


@router.patch("/{tag_id}", response_model=schemas.Tag)
def update_tag(
    tag_id: int,
    tag: schemas.TagUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_tag = service.get_tag(db, tag_id)
    if db_tag.tenant_id == 1 and user.role_id != 1: # only admin users can update a tag from tenant1
        raise PermissionDenied()
    updated_device = service.update_tag(db, db_tag, updated_tag=tag)
    if not updated_device:
        raise HTTPException(status_code=400, detail="El tag no pudo ser actualizado")
    return updated_device


@router.delete("/{tag_id}", response_model=schemas.TagDelete)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_tag = service.get_tag(db, tag_id)
    if db_tag.tenant_id == 1 and user.role_id != 1:
        raise PermissionDenied()
    deleted_tag_id = service.delete_tag(db, db_tag)
    if not deleted_tag_id:
        raise HTTPException(status_code=400, detail="El tag no pudo ser eliminado")
    return {
        "id": deleted_tag_id,
        "msg": f"Tag {deleted_tag_id} eliminado exitosamente!",
    }


@router.post("/delete", response_model=Dict[Any, Any])
def delete_tags(
    tags: List[schemas.Tag],
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_tags),
):
    tag_ids = list(map(lambda t: t.id, tags))
    deleted_tag_ids, deleted_rows = service.delete_tag_multi(db, user, tag_ids)
    return {
        "ids": deleted_tag_ids,
        "msg": f"{deleted_rows} Tags {deleted_tag_ids} eliminados exitosamente!",
    }
