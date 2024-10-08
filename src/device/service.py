import os
import time
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from src.auth.utils import create_otp, create_connection_url
from src.device import schemas, models, exceptions
from src.entity.service import create_entity_auto, update_entity_tags
from src.folder.models import Folder
from src.folder.service import check_folder_exist, get_folders
from src.tenant.models import tenants_and_users_table
from src.tenant.utils import filter_tag_ids
from src.user.service import get_user


def check_device_name_taken(
    db: Session, device_name: str, device_id: Optional[int] = None
):
    device = db.query(models.Device).filter(models.Device.name == device_name).first()
    if device:
        if device_id and device_id != device.id:
            raise exceptions.DeviceNameTaken()
        if not device_id:
            raise exceptions.DeviceNameTaken()


def get_device(db: Session, device_id: int) -> models.Device:
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise exceptions.DeviceNotFound()
    return device


# TODO: marking this function for deletion. check is not used anywhere first.
def get_devices_from_tenant(db: Session, tenant_id: int):
    return (
        db.query(models.Device)
        .filter(folder_models.Folder.id == models.Device.folder_id)
        .filter(folder_models.Folder.tenant_id == tenant_id)
    )


def expire_invalid_share_urls(db: Session) -> None:
    db.execute(
        update(models.Device)
        .where(models.Device.share_url.is_not(None))
        .where(models.Device.share_url_expires_at < datetime.now(UTC))
        .values(share_url=None, share_url_expires_at=None)
    )


def get_devices(db: Session, user_id: int):
    expire_invalid_share_urls(db)
    user = get_user(db, user_id)
    if user.is_admin:
        devices = select(models.Device)
    else:
        device_ids = user.get_device_ids()
        devices = select(models.Device).where(models.Device.id.in_(device_ids))
    return devices


def get_device_by_name(db: Session, device_name: str):
    device = db.query(models.Device).filter(models.Device.name == device_name).first()
    if not device:
        raise exceptions.DeviceNotFound()
    return device


def create_device(db: Session, device: schemas.DeviceCreate):
    # sanity checks
    if device.folder_id:
        check_folder_exist(db, device.folder_id)
    check_device_name_taken(db, device.name)

    entity = create_entity_auto(db)
    db_device = models.Device(**device.model_dump(), entity_id=entity.id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def update_device(
    db: Session, db_device: schemas.Device, updated_device: schemas.DeviceUpdate
) -> schemas.Device:
    # sanity checks
    values = updated_device.model_dump(exclude_unset=True)
    device = get_device(db, db_device.id)
    if updated_device.folder_id:
        check_folder_exist(db, updated_device.folder_id)
    check_device_name_taken(db, updated_device.name, device.id)

    if updated_device.tags or len(updated_device.tags) == 0:
        tags = values.pop("tags")
        tag_ids = filter_tag_ids(tags, device.folder.tenant_id)
        device.entity = update_entity_tags(
            db=db,
            entity=device.entity,
            tenant_ids=[device.folder.tenant_id],
            tag_ids=tag_ids,
        )
        db.commit()
    db.execute(
        update(models.Device).where(models.Device.id == device.id).values(values)
    )
    db.commit()
    db.refresh(device)
    return device


def update_device_heartbeat(db: Session, device_id: int, heartbeat: schemas.HeartBeat):
    # sanity checks
    values = heartbeat.model_dump(exclude_none=True)
    timestamp = datetime.now()
    values.update({"heartbeat_timestamp": timestamp})
    db.execute(
        update(models.Device).where(models.Device.id == device_id).values(values)
    )
    db.commit()
    return {"device_id": device_id, "timestamp": timestamp}


def delete_device(db: Session, db_device: schemas.Device):
    # sanity check
    get_device(db, db_device.id)

    db.delete(db_device)
    db.commit()
    return db_device.id


def create_share_url(
    user_id: int, device_id: int, expiration_hours: int
) -> tuple[schemas.ShareDeviceURL, datetime]:
    expiration_dt = datetime.now(UTC) + timedelta(hours=expiration_hours)
    to_encode = {
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": time.time(),
        "exp": expiration_dt,
    }
    share_hash = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    share_url = f"{os.getenv(f"API_SITE_DOMAIN_{os.getenv("ENV")}")}/devices/shared?id={share_hash}"
    return schemas.ShareDeviceURL(url=share_url), expiration_dt


def share_device(
    db: Session, user_id: int, device_id: int, share_params: schemas.ShareParams
) -> schemas.ShareDeviceURL:
    # extracting expiration_hours from share_params
    expiration_hours = share_params.expiration_hours
    if expiration_hours <= 0:
        raise exceptions.InvalidExpirationHours()

    # creating share_url with the corresponding response schema
    share_url, expiration_dt = create_share_url(user_id, device_id, expiration_hours)

    # updating device attributes (share_url + share exp time)
    device = get_device(db, device_id)
    device = update_device(
        db,
        device,
        schemas.DeviceUpdate(
            share_url=share_url.url,
            share_url_expires_at=expiration_dt,
            tags=device.tags,
        ),
    )

    return share_url


def verify_share_url(db: Session, token: str) -> str:
    # decoding data to obtain shared device metadata
    try:
        shared_device_metadata = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
    except ExpiredSignatureError as e:
        raise exceptions.ExpiredShareDeviceURL()

    # checking that the device share_url is not null
    device = db.scalars(
        select(models.Device)
        .where(models.Device.id == shared_device_metadata["device_id"])
        .where(models.Device.share_url.is_not(None))
    ).first()

    if not device:
        raise exceptions.DeviceNotFound()

    has_expired = datetime.now() > device.share_url_expires_at
    if has_expired:
        raise exceptions.ExpiredShareDeviceURL()

    # URL is valid, redirecting the user
    otp = create_otp()
    redirect_url = create_connection_url(db, device.id, otp)
    return redirect_url
