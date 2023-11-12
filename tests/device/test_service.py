from os import error
from pydantic import ValidationError
import pytest
from sqlalchemy.orm import Session
from src.device.exceptions import DeviceNameTakenError, DeviceNotFoundError

# from src.device.router import read_device
from src.device_group.exceptions import DeviceGroupNotFoundError
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
    device = create_device(session, DeviceCreate(name="dev5", device_group_id=1))
    assert device.name == "dev5"
    assert device.device_group_id == 1


def test_create_duplicated_device(session: Session) -> None:
    with pytest.raises(DeviceNameTakenError):
        device = create_device(session, DeviceCreate(name="dev1", device_group_id=1))


def test_create_incomplete_device(session: Session) -> None:
    with pytest.raises(ValidationError):
        device = create_device(session, DeviceCreate(name="dev1"))


def test_get_device(session: Session) -> None:
    device = get_device(session, device_id=1)
    assert device.name == "dev1"
    assert device.device_group_id == 1


def test_get_device_with_invalid_id(session: Session) -> None:
    with pytest.raises(DeviceNotFoundError):
        device = get_device(session, device_id=5)


def test_get_device_by_name(session: Session) -> None:
    device = get_device_by_name(session, device_name="dev1")
    assert device.name == "dev1"
    assert device.device_group_id == 1


def test_get_device_with_invalid_name(session: Session) -> None:
    with pytest.raises(DeviceNotFoundError):
        device = get_device_by_name(session, device_name="dev5")


def test_get_devices(session: Session) -> None:
    devices = get_devices(session)
    assert len(devices) >= 1


def test_update_device(session: Session) -> None:
    device = create_device(session, DeviceCreate(name="dev5", device_group_id=1))
    db_device = get_device(session, device.id)

    device = update_device(
        session,
        db_device=db_device,
        updated_device=DeviceUpdate(name="dev-custom", device_group_id=1),
    )
    assert device.name == "dev-custom"
    assert device.device_group_id == 1


def test_update_device_with_invalid_data(session: Session) -> None:
    device = create_device(session, DeviceCreate(name="dev5", device_group_id=1))
    db_device = get_device(session, device.id)

    with pytest.raises(DeviceGroupNotFoundError):
        device = update_device(
            session,
            db_device=db_device,
            updated_device=DeviceUpdate(name="dev-custom", device_group_id=5),
        )


def test_update_device_with_invalid_id(session: Session) -> None:
    db_device = get_device(session, 1)
    db_device.id = 5

    with pytest.raises(DeviceNotFoundError):
        device = update_device(
            session,
            db_device=db_device,
            updated_device=DeviceUpdate(name="dev-custom", device_group_id=1),
        )


def test_delete_device(session: Session) -> None:
    device = create_device(session, DeviceCreate(name="dev5delete", device_group_id=1))
    db_device = get_device(session, device.id)

    device_id = device.id
    deleted_device_id = delete_device(session, db_device=db_device)
    assert deleted_device_id == device_id

    with pytest.raises(DeviceNotFoundError):
        get_device(session, device.id)


def test_delete_device_with_invalid_id(session: Session) -> None:
    device = create_device(session, DeviceCreate(name="dev5delete", device_group_id=1))
    db_device = get_device(session, device.id)

    db_device.id = 5
    with pytest.raises(DeviceNotFoundError):
        deleted_device_id = delete_device(session, db_device=db_device)
