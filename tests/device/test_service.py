import pytest
from sqlalchemy.orm import Session
from src.device.router import read_device
from tests.database import session
from src.device.service import (
    create_device,
    get_device,
    get_device_by_name,
    get_devices,
    delete_device,
    update_device,
)
from src.device.schemas import DeviceCreate, DeviceDelete, DeviceUpdate


def test_create_device(session: Session) -> None:
    device = create_device(session, DeviceCreate(name="dev2", device_group_id=1))
    assert device.name == "dev2"
    assert device.device_group_id == 1


def test_get_device(session: Session) -> None:
    device = get_device(session, device_id=1)
    assert device.name == "dev1"
    assert device.device_group_id == 1


def test_get_device_by_name(session: Session) -> None:
    device = get_device_by_name(session, device_name="dev1")
    assert device.name == "dev1"
    assert device.device_group_id == 1


def test_get_devices(session: Session) -> None:
    devices = get_devices(session)
    assert len(devices) >= 1

def test_update_device(session: Session) -> None:
    device = create_device(session, DeviceCreate(name="dev2", device_group_id=1))
    db_device = read_device(device.id, session)

    device = update_device(
        session,
        db_device=db_device,
        updated_device=DeviceUpdate(name="dev-custom", device_group_id=1),
    )
    assert device.name == "dev-custom"
    assert device.device_group_id == 1


def test_delete_device(session: Session) -> None:
    device = create_device(session, DeviceCreate(name="dev2delete", device_group_id=1))
    db_device = read_device(device.id, session)

    device_id = device.id
    deleted_device_id = delete_device(session, db_device=db_device)
    assert deleted_device_id == device_id

    with pytest.raises(Exception):
        read_device(device.id, session)
