from src.schemas import UserGroupWithUsers, UserWithUserGroups
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter()


@router.post("/user_groups/", response_model=UserGroupWithUsers)
def create_user_group(
    user_group: schemas.UserGroupCreate, db: Session = Depends(get_db)
):
    db_user_group = service.create_user_group(db=db, user_group=user_group)
    return db_user_group


@router.get("/user_groups/{user_group_id}", response_model=UserGroupWithUsers)
def read_user_group(user_group_id: int, db: Session = Depends(get_db)):
    db_user_group = service.get_user_group(db, user_group_id=user_group_id)
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


@router.patch("/user_groups/{user_group_id}/users", response_model=UserGroupWithUsers)
def add_users(
    user_group_id: int,
    users: list[UserWithUserGroups],
    db: Session = Depends(get_db),
):
    db_user_group = read_user_group(user_group_id, db)
    updated_db_user_group = service.add_users(
        db=db, db_user_group=db_user_group, users=users
    )
    return updated_db_user_group


@router.patch("/user_groups/{user_group_id}/users/delete", response_model=UserGroupWithUsers)
def delete_users(
    user_group_id: int,
    users_to_delete: list[UserWithUserGroups],
    db: Session = Depends(get_db),
):
    db_user_group = read_user_group(user_group_id, db)
    db_user_group = service.delete_users(
        db=db, db_user_group=db_user_group, users_to_delete=users_to_delete
    )
    return db_user_group


@router.get(
    "/user_groups/{user_group_id}/users", response_model=list[UserWithUserGroups]
)
def get_users_from_user_group(user_group_id: int, db: Session = Depends(get_db)):
    db_users_from_group = service.get_users_from_group(db, user_group_id)
    return db_users_from_group
