from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from fastapi_pagination.ext.sqlalchemy import paginate
from src.auth.dependencies import get_current_active_user
from src.user.schemas import User
from src.database import get_db
from src.role import service, schemas
from src.utils import CustomBigPage

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=schemas.Role)
def create_role(
    role: schemas.RoleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_role = service.create_role(db=db, role=role)
    return db_role


@router.get("/{role_id}", response_model=schemas.Role)
def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_role = service.get_role(db, role_id=role_id)
    return db_role


@router.get("/", response_model=CustomBigPage[schemas.Role])
def read_roles(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    return paginate(db, service.get_roles(db, user.id))


@router.patch("/{role_id}", response_model=schemas.Role)
def update_role(
    role_id: int,
    role: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_role = read_role(role_id, db)
    updated_role = service.update_role(db, db_role, updated_role=role)

    return updated_role


@router.delete("/{role_id}", response_model=schemas.RoleDelete)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    db_role = read_role(role_id, db)
    deleted_role_id = service.delete_role(db, db_role)

    return {
        "id": deleted_role_id,
        "msg": f"Rol {deleted_role_id} eliminado exitosamente!",
    }
