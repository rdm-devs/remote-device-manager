import os
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import List
from src.auth.dependencies import (
    get_current_active_user,
    has_admin_role,
    has_access_to_tenant,
    has_access_to_device,
    has_admin_or_owner_role,
    can_edit_device,
)
from src.auth.utils import create_connection_url, create_otp
from src.auth.schemas import ConnectionUrl
from src.user.schemas import User
from src.tenant.router import router as tenant_router
from src.database import get_db
from src.device import service, schemas, utils
from src.utils import CustomBigPage

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=schemas.Device)
def register_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(has_admin_or_owner_role),
):
    if device.serial_number is not None:
        db_device = utils.get_device_by_serial_number(db, device.serial_number)
        if db_device:
            return update_device(db_device.id, device, db, user)
    db_device = service.create_device(db=db, device=device)
    return db_device


@router.get("/shared")
def connect_to_shared_device(id: str, db: Session = Depends(get_db)):
    redirect_url = service.verify_share_url(db, id)
    return RedirectResponse(redirect_url)


@router.get("/unassigned", response_model=CustomBigPage[schemas.DeviceList])
def get_unassigned_devices(
    db: Session = Depends(get_db), user: User = Depends(has_admin_or_owner_role)
):
    unassigned_devices = service.get_unassigned_devices(db)
    return paginate(db, unassigned_devices)


# TODO: remove
# @router.get("/verify-url")
# def connect_to_shared_device(url: str, db: Session = Depends(get_db)):
#     try:
#         redirect_url = service.verify_share_url(db, url.split("?id=")[1])
#         return True if redirect_url else False
#     except:
#         return False


@router.get("/{device_id:int}", response_model=schemas.Device)
def read_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    db_device = service.get_device(db, device_id=device_id)
    return db_device


@router.get("/", response_model=CustomBigPage[schemas.DeviceList])
def read_devices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return paginate(db, service.get_devices(db, user.id))


@router.patch("/{device_id}", response_model=schemas.Device)
def update_device(
    device_id: int,
    device: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_device),
):
    db_device = read_device(device_id, db)
    updated_device = service.update_device(db, db_device, updated_device=device)

    return updated_device


@router.delete("/{device_id}", response_model=schemas.DeviceDelete)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_device),
):
    db_device = read_device(device_id, db)
    deleted_device_id = service.delete_device(db, db_device)

    return {
        "id": deleted_device_id,
        "msg": f"Device {deleted_device_id} removed succesfully!",
    }


@router.get("/{device_id}/connect", response_model=ConnectionUrl)
async def connect(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    otp = create_otp()
    url = create_connection_url(db, device_id, otp)
    return {"url": url}


@router.post("/{device_id}/heartbeat", response_model=schemas.HeartBeatResponse)
def update_heartbeat(
    device_id: int,
    heartbeat: schemas.HeartBeat,
    db: Session = Depends(get_db),
):
    device_status = service.update_device_heartbeat(db, device_id, heartbeat)
    return device_status


@router.post("/{device_id}/share", response_model=schemas.ShareDeviceURL)
def share_device(
    device_id: int,
    share_params: schemas.ShareParams,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    share_url = service.share_device(db, user.id, device_id, share_params)
    return share_url


@router.get("/{device_id:int}/revoke-share-url", response_model=schemas.Device)
def revoke_share_url(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    return service.revoke_share_url(db, device_id)
