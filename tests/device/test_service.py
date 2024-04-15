from pydantic import ValidationError
import pytest
from sqlalchemy.orm import Session
from src.device.exceptions import DeviceNameTaken, DeviceNotFound
from src.folder.exceptions import FolderNotFound
from tests.database import session, mock_os_data, mock_vendor_data
from src.device.service import (
    create_device,
    get_device,
    get_device_by_name,
    get_devices,
    delete_device,
    update_device,
)
from src.device.schemas import DeviceCreate, DeviceDelete, DeviceUpdate

TEST_MAC_ADDR = "61:68:0C:1E:93:7F"
TEST_IP_ADDR = "96.119.132.46"


def test_create_device(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5",
            folder_id=1,
            os_id=1,
            vendor_id=1,
            mac_address=TEST_MAC_ADDR,
            ip_address=TEST_IP_ADDR,
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    assert device.name == "dev5"
    assert device.folder_id == 1


def test_create_duplicated_device(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    with pytest.raises(DeviceNameTaken):
        device = create_device(
            session,
            DeviceCreate(
                name="dev1",
                folder_id=1,
                os_id=1,
                vendor_id=1,
                mac_address=TEST_MAC_ADDR,
                ip_address=TEST_IP_ADDR,
                **mock_os_data,
                **mock_vendor_data
            ),
        )


def test_create_incomplete_device(session: Session) -> None:
    with pytest.raises(ValidationError):
        device = create_device(session, DeviceCreate(name="dev1"))


def test_get_device(session: Session) -> None:
    device = get_device(session, device_id=1)
    assert device.name == "dev1"
    assert device.folder_id == 1


def test_get_device_with_invalid_id(session: Session) -> None:
    with pytest.raises(DeviceNotFound):
        device = get_device(session, device_id=5)


def test_get_device_by_name(session: Session) -> None:
    device = get_device_by_name(session, device_name="dev1")
    assert device.name == "dev1"
    assert device.folder_id == 1


def test_get_device_with_invalid_name(session: Session) -> None:
    with pytest.raises(DeviceNotFound):
        device = get_device_by_name(session, device_name="dev5")


def test_get_devices(session: Session) -> None:
    devices = get_devices(session, user_id=1).all()  # admin
    assert len(devices) == 3

    devices_owner_2 = get_devices(session, user_id=2).all()  # owner
    assert len(devices_owner_2) == 2

    devices_user = get_devices(session, user_id=4).all()  # user
    assert len(devices_user) == 2
    assert devices_owner_2 == devices_user

    devices = get_devices(session, user_id=3).all()  # owner
    assert len(devices) == 1


def test_update_device(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5",
            folder_id=1,
            os_id=1,
            vendor_id=1,
            mac_address=TEST_MAC_ADDR,
            ip_address=TEST_IP_ADDR,
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    db_device = get_device(session, device.id)

    device = update_device(
        session,
        db_device=db_device,
        updated_device=DeviceUpdate(name="dev-custom"),
    )
    assert device.name == "dev-custom"
    assert device.folder_id == 1


def test_update_device_with_invalid_data(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5",
            folder_id=1,
            os_id=1,
            vendor_id=1,
            mac_address=TEST_MAC_ADDR,
            ip_address=TEST_IP_ADDR,
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    db_device = get_device(session, device.id)

    folder_id = 6  # this folder id must not exist
    with pytest.raises(FolderNotFound):
        device = update_device(
            session,
            db_device=db_device,
            updated_device=DeviceUpdate(name="dev-custom", folder_id=folder_id),
        )


def test_update_device_with_invalid_id(session: Session) -> None:
    db_device = get_device(session, 1)
    db_device.id = 5

    with pytest.raises(DeviceNotFound):
        device = update_device(
            session,
            db_device=db_device,
            updated_device=DeviceUpdate(name="dev-custom", folder_id=1),
        )


def test_delete_device(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5delete",
            folder_id=1,
            os_id=1,
            vendor_id=1,
            mac_address=TEST_MAC_ADDR,
            ip_address=TEST_IP_ADDR,
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    db_device = get_device(session, device.id)

    device_id = device.id
    deleted_device_id = delete_device(session, db_device=db_device)
    assert deleted_device_id == device_id

    with pytest.raises(DeviceNotFound):
        get_device(session, device.id)


def test_delete_device_with_invalid_id(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5delete",
            folder_id=1,
            os_id=1,
            vendor_id=1,
            mac_address=TEST_MAC_ADDR,
            ip_address=TEST_IP_ADDR,
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    db_device = get_device(session, device.id)

    db_device.id = 5
    with pytest.raises(DeviceNotFound):
        deleted_device_id = delete_device(session, db_device=db_device)
