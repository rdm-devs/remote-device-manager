import os
from fastapi import Depends, APIRouter, HTTPException, Path, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import List, Union
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
from src.device import service, schemas, utils, models, exceptions
from src.utils import CustomBigPage

router = APIRouter(prefix="/devices", tags=["devices"])
alt_router = APIRouter(prefix="/serials", tags=["serials"])  # compatibilidad para SIA


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


@router.get("/unassigned", response_model=CustomBigPage[schemas.Device])
def get_unassigned_devices(
    db: Session = Depends(get_db), user: User = Depends(has_admin_or_owner_role)
):
    unassigned_devices = service.get_unassigned_devices(db)
    return paginate(
        db,
        unassigned_devices,
        transformer=lambda devices: service.device_transformer(db, devices),
    )


@alt_router.get("/{serial_number}", response_model=schemas.Device)
def read_device_with_serial_number(
    serial_number: str,
    db: Session = Depends(get_db),
    user: User = Depends(lambda serial_number: has_access_to_device(serial_number)),
):
    return read_device(serial_number, db)


@router.get("/{device_id}", response_model=schemas.Device)
def read_device(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    if str(device_id).isdigit():
        return service.get_device(db, device_id=device_id)
    device = utils.get_device_by_serial_number(db, serial_number=device_id)
    if not device:
        raise exceptions.DeviceNotFound()
    return device


@router.get("/", response_model=CustomBigPage[schemas.DeviceList])
def read_devices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return paginate(
        db,
        service.get_devices(db, user.id),
        transformer=lambda devices: service.device_transformer(db, devices),
    )


@router.patch("/{device_id}", response_model=schemas.Device)
def update_device(
    device_id: Union[str, int],
    device: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_device),
):
    db_device = read_device(device_id, db)
    updated_device = service.update_device(db, db_device, updated_device=device)

    return updated_device


@router.delete("/{device_id}", response_model=schemas.DeviceDelete)
def delete_device(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    user: User = Depends(can_edit_device),
):
    db_device = read_device(device_id, db)
    deleted_device_id, deleted_device_serial_number = service.delete_device(
        db, db_device
    )

    return {
        "id": deleted_device_id,
        "serial_number": deleted_device_serial_number,
        "msg": f"Dispositivo {deleted_device_serial_number} eliminado exitosamente!",
    }


@alt_router.get("/{serial_number}/connect", response_model=ConnectionUrl)
async def connect_with_serial_number(
    serial_number: str,
    db: Session = Depends(get_db),
    user: User = Depends(lambda serial_number: has_access_to_device(serial_number)),
):
    return await connect(serial_number, db)


@router.get("/{device_id}/connect", response_model=ConnectionUrl)
async def connect(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    otp = create_otp()
    url = create_connection_url(db, device_id, otp)
    return {"url": url}


@router.post("/{device_id}/heartbeat", response_model=schemas.HeartBeatResponse)
def update_heartbeat(
    device_id: Union[str, int],
    heartbeat: schemas.HeartBeat,
    db: Session = Depends(get_db),
):
    device_status = service.update_device_heartbeat(db, device_id, heartbeat)
    return device_status


@router.post("/{device_id}/share", response_model=schemas.ShareDeviceURL)
def share_device(
    device_id: Union[str, int],
    share_params: schemas.ShareParams,
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    return service.share_device(db, user.id, device_id, share_params)


@router.get("/{device_id}/revoke-share-url", response_model=schemas.Device)
def revoke_share_url(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    user: User = Depends(has_access_to_device),
):
    return service.revoke_share_url(db, device_id)


# @router.get("/{device_id:int}/heartbeats")
# def get_device_heartbeats(
#     device_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(has_access_to_device),
# ):
#     return service.read_device_heartbeats(db, device_id)
