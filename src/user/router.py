from src.schemas import UserWithUserGroups
from . import service, schemas
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()


@router.post("/users/", response_model=UserWithUserGroups)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # sanity check:
    service.check_email_exists(db, email=user.email)

    db_user = service.create_user(db=db, user=user)
    return db_user


@router.get("/users/", response_model=list[UserWithUserGroups])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserWithUserGroups)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = service.get_user(db, user_id=user_id)
    return db_user


@router.patch("/users/{user_id}", response_model=UserWithUserGroups)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = read_user(user_id, db)
    updated_user = service.update_user(db, db_user, updated_user=user)
    return updated_user


@router.delete("/users/{user_id}", response_model=schemas.UserDelete)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = read_user(user_id, db)
    deleted_user_user_id = service.delete_user(db, db_user)
    if not deleted_user_user_id:
        raise HTTPException(status_code=400, detail="User could not be deleted")
    return {
        "id": deleted_user_user_id,
        "msg": f"User {deleted_user_user_id} removed succesfully!",
    }
