from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.auth.dependencies import get_current_active_user
from . import service, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


# @router.post("/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     # sanity check:
#     service.check_email_exists(db, email=user.email)

#     db_user = service.create_user(db=db, user=user)
#     return db_user


@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    users = service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    db_user = service.get_user(db, user_id=user_id)
    return db_user


@router.patch("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_active_user),
):
    db_user = read_user(user_id, db)
    updated_user = service.update_user(db, db_user, updated_user=user)
    return updated_user


@router.delete("/{user_id}", response_model=schemas.UserDelete)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    db_user = read_user(user_id, db)
    deleted_user_user_id = service.delete_user(db, db_user)
    if not deleted_user_user_id:
        raise HTTPException(status_code=400, detail="User could not be deleted")
    return {
        "id": deleted_user_user_id,
        "msg": f"User {deleted_user_user_id} removed succesfully!",
    }


@router.patch("/{user_id}/role", response_model=schemas.UserRole)
def assign_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_role),
):
    service.assign_role(db=db, user_id=user_id, role_id=role_id)
    return schemas.UserRole(id=user_id, role_id=role_id)
