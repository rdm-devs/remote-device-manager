import os
import time
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from typing import Optional, Union, Sequence
from sqlalchemy import select, update, insert
from sqlalchemy.orm import Session
from src.auth.utils import create_otp, create_connection_url
from src.device import schemas, models, exceptions, utils
from src.entity.service import create_entity_auto, update_entity_tags
from src.folder.models import Folder
from src.folder.service import check_folder_exist, get_folders, get_root_folder
from src.tenant.models import tenants_and_users_table, TenantSettings
from src.tenant.service import get_tenant_settings
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


def expire_invalid_share_urls(db: Session, device_id: Union[int, None] = None) -> None:
    update_stmt = (
        update(models.Device)
        .where(models.Device.share_url.is_not(None))
        .where(models.Device.share_url_expires_at < datetime.now())
    )
    if device_id:
        update_stmt = update_stmt.where(models.Device.id == device_id)

    db.execute(update_stmt.values(share_url=None, share_url_expires_at=None))
    db.commit()


def get_device(db: Session, device_id: int) -> models.Device:
    expire_invalid_share_urls(db, device_id=device_id)
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise exceptions.DeviceNotFound()
    return device


def get_devices(db: Session, user_id: int):
    expire_invalid_share_urls(db)
    user = get_user(db, user_id)
    if user.is_admin:
        devices = select(models.Device)
    else:
        device_ids = user.get_device_ids()
        devices = select(models.Device).where(models.Device.id.in_(device_ids))

    latest_heartbeat = (
        select(models.Heartbeat)
        .order_by(models.Heartbeat.timestamp.desc())
        .limit(1)
        .subquery()
    )
    stmt = (
        devices.add_columns(
            latest_heartbeat.c.timestamp.label("heartbeat_timestamp")
        )  # creating an alias that matches the schema attr.
        .join(latest_heartbeat, isouter=True)
        .group_by(models.Device.id)
    )

    return stmt.select()


def get_unassigned_devices(db: Session):
    expire_invalid_share_urls(db)
    folder_id = db.scalar(select(Folder.id).where(Folder.tenant_id == 1))
    devices = select(models.Device).where(models.Device.folder_id == folder_id)

    latest_heartbeat = (
        select(models.Heartbeat)
        .order_by(models.Heartbeat.timestamp.desc())
        .limit(1)
        .subquery()
    )
    stmt = (
        devices.add_columns(
            latest_heartbeat.c.timestamp.label("heartbeat_timestamp")
        )  # creating an alias that matches the schema attr.
        .join(latest_heartbeat, isouter=True)
        .group_by(models.Device.id)
    )

    return stmt.select()


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
    tags = values.pop("tags", None)
    if updated_device.folder_id:
        check_folder_exist(db, updated_device.folder_id)
    check_device_name_taken(db, updated_device.name, device.id)

    if tags is not None and len(tags) >= 0:
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


def update_device_heartbeat(
    db: Session, device_id: Union[str, int], heartbeat: schemas.HeartBeat
):
    # sanity checks
    values = heartbeat.model_dump(exclude_none=True)
    id_rust = values.pop("id_rust", None)
    pass_rust = values.pop("pass_rust", None)
    if not str(device_id).isdigit():
        device = utils.get_device_by_serial_number(db, device_id)
        device_id = device.id

    timestamp = datetime.now()
    db.execute(
        insert(models.Heartbeat).values(
            {"device_id": device_id, "timestamp": timestamp, **values}
        ),
    )
    db.commit()

    if id_rust is not None and pass_rust is not None:
        # the attributes are not valid when equal to None so no modification is done.
        device_update = schemas.DeviceUpdate(id_rust=id_rust, pass_rust=pass_rust)
        db.execute(
            update(models.Device)
            .where(models.Device.id == device_id)
            .values(**device_update.model_dump(exclude_unset=True))
        )
        db.commit()

    # updating heartbeat frequency according to tenant settings
    db_device: models.Device = db.scalar(
        select(models.Device).where(models.Device.id == device_id)
    )
    tenant_settings = get_tenant_settings(db, db_device.folder.tenant_id)
    return schemas.HeartBeatResponse(
        device_id=device_id,
        timestamp=timestamp,
        heartbeat_s=tenant_settings.heartbeat_s,
    )


def delete_device(db: Session, db_device: schemas.Device):
    # sanity check
    get_device(db, db_device.id)

    # deleting tags from the current folder tenant before moving it to another folder
    current_folder_tenant_id = db_device.folder.tenant_id
    current_tags = db_device.tags
    db_device.entity.tags = [t for t in current_tags if t.tenant_id != current_folder_tenant_id]
    db.commit()

    # assigning tenant1's root folder id as folder_id for this device 
    root_folder = get_root_folder(db, tenant_id=1)
    updated_device = update_device(db, db_device, schemas.DeviceUpdate(folder_id=root_folder.id))

    db.refresh(updated_device)
    return updated_device.id, updated_device.serial_number


def format_expiration_date(expiration_date: datetime) -> datetime:
    date_format = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(expiration_date.strftime(date_format), date_format)


def create_share_url(
    user_id: int, device_id: Union[str, int], expiration_minutes: int
) -> tuple[str, datetime]:
    expiration_minutes = (
        int(os.getenv("SHARE_URL_MAX_DURATION_MINUTES"))
        if expiration_minutes == 0
        else expiration_minutes
    )
    expiration_dt = format_expiration_date(
        datetime.now(UTC) + timedelta(minutes=expiration_minutes)
    )
    to_encode = {
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": time.time(),
        "exp": expiration_dt,
    }
    share_hash = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    share_url = f"{os.getenv(f"DEVICE_SHARE_URL_BASE_{os.getenv("ENV")}")}/devices/shared?id={share_hash}"
    return share_url, expiration_dt


def share_device(
    db: Session,
    user_id: int,
    device_id: Union[str, int],
    share_params: schemas.ShareParams,
) -> schemas.ShareDeviceURL:
    # extracting expiration_minutes from share_params
    expiration_minutes = share_params.expiration_minutes
    if expiration_minutes < 0:
        raise exceptions.InvalidExpirationMinutes()

    # updating device attributes (share_url + share exp time)
    if str(device_id).isdigit():
        device = get_device(db, device_id)
    else:
        device = utils.get_device_by_serial_number(db, device_id)

    if not device.id_rust or not device.pass_rust:
        raise exceptions.DeviceCredentialsNotConfigured()

    # creating share_url with the corresponding response schema
    share_url, expiration_dt = create_share_url(user_id, device_id, expiration_minutes)
    device = update_device(
        db,
        device,
        schemas.DeviceUpdate(
            share_url=share_url,
            share_url_expires_at=expiration_dt,
            tags=device.tags,
        ),
    )

    return schemas.ShareDeviceURL(
        url=share_url, expiration_date=expiration_dt, time_zone=device.time_zone
    )


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
        .where(models.Device.share_url.contains(token))
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


def revoke_share_url(db: Session, device_id: Union[str, int]) -> schemas.Device:
    if str(device_id).isdigit():
        device = get_device(db, device_id)
    else:
        device = utils.get_device_by_serial_number(db, device_id)

    device = update_device(
        db,
        device,
        schemas.DeviceUpdate(
            share_url=None,
            share_url_expires_at=None,
            tags=device.tags,
        ),
    )

    return device


def append_online_status_column(db: Session, device: models.Device):
    return {
        **device._asdict(),
        # "is_online": utils.get_online_status(get_device(db, device[0])),
        "is_online": get_device(db, device[0]).is_online,
    }


def device_transformer(
    db: Session, devices: Sequence[models.Device]
) -> Sequence[models.Device]:
    return [append_online_status_column(db, device) for device in devices]


def read_device_heartbeats(db: Session, device_id: int):
    heartbeats = db.scalars(
        select(models.Heartbeat)
        .where(models.Heartbeat.device_id == device_id)
        .order_by(models.Heartbeat.timestamp.desc())
    ).all()
    return heartbeats
