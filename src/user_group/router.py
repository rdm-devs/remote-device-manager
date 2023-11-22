from src.schemas import UserGroupWithUsers
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter()


@router.post("/user_groups/", response_model=UserGroupWithUsers)
def create_user_group(
    user_group: schemas.UserGroupCreate, db: Session = Depends(get_db)
):
    db_user_group = service.get_user_group_by_name(db, name=user_group.name)
    if db_user_group:
        raise HTTPException(status_code=400, detail="UserGroup name already registered")
    return service.create_user_group(db=db, user_group=user_group)


@router.get("/user_groups/{group_id}", response_model=UserGroupWithUsers)
def read_user_group(group_id: int, db: Session = Depends(get_db)):
    db_user_group = service.get_user_group(db, group_id=group_id)
    if db_user_group is None:
        raise HTTPException(status_code=404, detail="UserGroup not found")
    return db_user_group


@router.get("/user_groups/", response_model=list[UserGroupWithUsers])
def read_user_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_user_groups(db, skip=skip, limit=limit)


@router.patch("/user_groups/{group_id}", response_model=UserGroupWithUsers)
def update_user_group(
    group_id: int, user_group: schemas.UserGroupUpdate, db: Session = Depends(get_db)
):
    db_user_group = read_user_group(group_id, db)
    updated_user_group = service.update_user_group(
        db, db_user_group, updated_user_group=user_group
    )
    if not updated_user_group:
        raise HTTPException(status_code=400, detail="UserGroup could not be updated")
    return updated_user_group


@router.delete("/user_groups/{group_id}", response_model=schemas.UserGroupDelete)
def delete_user_group(group_id: int, db: Session = Depends(get_db)):
    db_user_group = read_user_group(group_id, db)
    deleted_user_group_id = service.delete_user_group(db, db_user_group)
    if not deleted_user_group_id:
        raise HTTPException(status_code=400, detail="UserGroup could not be deleted")
    return {
        "id": deleted_user_group_id,
        "msg": f"UserGroup {deleted_user_group_id} removed succesfully!",
    }
