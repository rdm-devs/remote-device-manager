from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter()


@router.post("/device_groups/", response_model=schemas.DeviceGroup)
def create_device_group(device_group: schemas.DeviceGroupCreate, db: Session = Depends(get_db)):
    db_device_group = service.create_device_group(db, device_group)
    return db_device_group


@router.get("/device_groups/{device_group_id}", response_model=schemas.DeviceGroup)
def read_device_group(device_group_id: int, db: Session = Depends(get_db)):
    db_device_group = service.get_device_group(db, device_group_id)
    return db_device_group

@router.get("/device_groups/", response_model=list[schemas.DeviceGroup])
def read_device_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_device_groups(db, skip=skip, limit=limit)

@router.patch("/device_groups/{device_group_id}", response_model=schemas.DeviceGroup)
def update_device_group(
    device_group_id: int, device_group: schemas.DeviceGroupUpdate, db: Session = Depends(get_db)
):
    db_device_group = read_device_group(device_group_id, db)
    updated_device = service.update_device_group(db, db_device_group, updated_device_group=device_group)
    if not updated_device:
        raise HTTPException(status_code=400, detail="Device group could not be updated")
    return updated_device


@router.delete("/device_groups/{device_group_id}", response_model=schemas.DeviceGroupDelete)
def delete_device(device_group_id: int, db: Session = Depends(get_db)):
    db_device_group_group = read_device_group(device_group_id, db)
    deleted_device_group_id = service.delete_device_group(db, db_device_group_group)
    if not deleted_device_group_id:
        raise HTTPException(status_code=400, detail="UserGroup could not be deleted")
    return {
        "id": deleted_device_group_id,
        "msg": f"Device group {deleted_device_group_id} removed succesfully!",
    }
