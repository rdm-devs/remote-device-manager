from pydantic import ValidationError
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.device.exceptions import (
    DeviceNameTaken,
    DeviceNotFound,
    InvalidExpirationMinutes,
    ExpiredShareDeviceURL,
)
from src.folder.exceptions import FolderNotFound
from tests.database import session, mock_os_data, mock_vendor_data
from src.device.service import (
    create_device,
    get_device,
    get_device_by_name,
    get_devices,
    delete_device,
    update_device,
    share_device,
    verify_share_url,
    create_share_url,
    update_device_heartbeat,
    read_device_heartbeats,
)
from src.device.utils import get_device_by_serial_number
from src.device.schemas import (
    DeviceCreate,
    DeviceDelete,
    DeviceUpdate,
    ShareParams,
    Device,
    HeartBeat,
)
from src.tenant.service import get_tenant
from src.tag.models import entities_and_tags_table
from src.tag.service import get_tags
from src.user.service import get_user

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
            MAC_addresses=TEST_MAC_ADDR,
            local_ips=TEST_IP_ADDR,
            time_zone="America/Argentina/Buenos_Aires",
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
                MAC_addresses=TEST_MAC_ADDR,
                local_ips=TEST_IP_ADDR,
                time_zone="America/Argentina/Buenos_Aires",
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
    assert device.folder_id == 3


def test_get_device_with_invalid_id(session: Session) -> None:
    with pytest.raises(DeviceNotFound):
        device = get_device(session, device_id=5)


def test_get_device_by_name(session: Session) -> None:
    device = get_device_by_name(session, device_name="dev1")
    assert device.name == "dev1"
    assert device.folder_id == 3


def test_get_device_with_invalid_name(session: Session) -> None:
    with pytest.raises(DeviceNotFound):
        device = get_device_by_name(session, device_name="dev5")


def test_get_devices(session: Session) -> None:
    devices = session.execute(get_devices(session, user_id=1)).fetchall()  # admin
    assert len(devices) == 3

    devices_owner_2 = session.execute(
        get_devices(session, user_id=2)
    ).fetchall()  # owner
    assert len(devices_owner_2) == 2

    devices_user = session.execute(get_devices(session, user_id=4)).fetchall()  # user
    assert len(devices_user) == 2
    assert devices_owner_2 == devices_user

    devices = session.execute(get_devices(session, user_id=3)).fetchall()  # owner
    assert len(devices) == 1


def test_update_device(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5",
            folder_id=3,
            os_id=1,
            vendor_id=1,
            MAC_addresses=TEST_MAC_ADDR,
            local_ips=TEST_IP_ADDR,
            time_zone="America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    db_device = get_device(session, device.id)

    tenant_id = 1
    tenant_1 = get_tenant(session, tenant_id)

    device = update_device(
        session,
        db_device=db_device,
        updated_device=DeviceUpdate(name="dev-custom", tags=tenant_1.tags),
    )
    assert device.name == "dev-custom"
    assert device.folder_id == 3
    assert all(t in device.tags for t in tenant_1.tags)

    tenant_id = 2
    tenant_2 = get_tenant(session, tenant_id)

    device = update_device(
        session,
        db_device=db_device,
        updated_device=DeviceUpdate(tags=[*device.tags, *tenant_2.tags]),
    )

    assert all(t not in device.tags for t in tenant_2.tags)
    assert all(t in device.tags for t in tenant_1.tags)

    # testing associative relationship (Entity-Tag) is working
    query = select(entities_and_tags_table.c.tag_id).where(
        entities_and_tags_table.c.entity_id == device.entity_id,
    )
    relationship_tag_ids = session.scalars(query).all()
    assert relationship_tag_ids is not None
    assert all(t.id in relationship_tag_ids for t in device.tags)


def test_update_device_with_invalid_data(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5",
            folder_id=3,
            os_id=1,
            vendor_id=1,
            MAC_addresses=TEST_MAC_ADDR,
            local_ips=TEST_IP_ADDR,
            time_zone="America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    db_device = get_device(session, device.id)

    folder_id = 16  # this folder id must not exist
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
            updated_device=DeviceUpdate(name="dev-custom", folder_id=3),
        )


def test_update_device_to_remove_all_tags(session: Session) -> None:
    db_device = get_device(session, 1)
    tenant_id = 1
    tenant_1 = get_tenant(session, tenant_id)

    # updating device to add tenant_1's tags
    device = update_device(
        session,
        db_device=db_device,
        updated_device=DeviceUpdate(
            name="dev-custom", tags=[*db_device.tags, *tenant_1.tags]
        ),
    )
    assert device.name == "dev-custom"
    assert device.folder_id == 3
    assert all(t in device.tags for t in tenant_1.tags)

    # updating device to delete all its tags
    device = update_device(
        session,
        db_device=db_device,
        updated_device=DeviceUpdate(name="dev-custom", tags=[]),
    )
    assert device.name == "dev-custom"
    assert device.folder_id == 3
    assert len(device.tags) == 0


def test_move_device_to_another_folder(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5",
            folder_id=2,
            os_id=1,
            vendor_id=1,
            MAC_addresses=TEST_MAC_ADDR,
            local_ips=TEST_IP_ADDR,
            time_zone="America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    assert device.folder_id == 2
    updated_device = update_device(session, device, DeviceUpdate(folder_id=1))
    assert updated_device.folder_id == 1

@pytest.mark.asyncio
async def test_delete_device(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    admin_user = get_user(session, user_id=1)
    tags_tenant_2 = await get_tags(session, auth_user=admin_user, user_id=1, tenant_id=2) 
    device = create_device(
        session,
        DeviceCreate(
            name="dev5delete",
            folder_id=6, # folder_id=6 belongs to tenant 2. see tests/database.py
            os_id=1,
            vendor_id=1,
            MAC_addresses=TEST_MAC_ADDR,
            local_ips=TEST_IP_ADDR,
            time_zone="America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    # assigning tags from tenant 2
    device = update_device(session, device, DeviceUpdate(tags=tags_tenant_2))

    # confirming that after deletion, device is moved to tenant1's root folder
    deleted_device_id = delete_device(session, db_device=device)
    assert deleted_device_id == device.id
    device = get_device(session, device.id)
    assert device.folder_id == 1 # folder_id=1 is root folder for tenant1. see tests/database.py
    # confirming previoust tenant's related tags were removed from device's tags.
    assert all(t not in tags_tenant_2 for t in device.tags)


def test_delete_device_with_invalid_id(
    session: Session, mock_os_data: dict, mock_vendor_data: dict
) -> None:
    device = create_device(
        session,
        DeviceCreate(
            name="dev5delete",
            folder_id=3,
            os_id=1,
            vendor_id=1,
            MAC_addresses=TEST_MAC_ADDR,
            local_ips=TEST_IP_ADDR,
            time_zone="America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    db_device = get_device(session, device.id)

    db_device.id = 5
    with pytest.raises(DeviceNotFound):
        deleted_device_id = delete_device(session, db_device=db_device)


def test_share_device(session: Session) -> None:
    share_data = share_device(session, 1, 1, ShareParams(expiration_minutes=1))
    assert share_data.url is not None
    assert share_data.expiration_date is not None
    assert share_data.time_zone is not None


def test_share_device_with_invalid_expiration_minutes(session: Session) -> None:
    with pytest.raises(InvalidExpirationMinutes):
        share_data = share_device(session, 1, 1, ShareParams(expiration_minutes=-1))


def test_share_device_with_invalid_device_id(session: Session) -> None:
    with pytest.raises(DeviceNotFound):
        share_data = share_device(session, 1, -1, ShareParams(expiration_minutes=1))


def test_verify_share_url(session: Session) -> None:
    share_data = share_device(session, 1, 1, ShareParams(expiration_minutes=1))
    assert share_data.url is not None
    assert share_data.expiration_date is not None
    assert share_data.time_zone is not None

    redirect_url = verify_share_url(session, share_data.url.split("id=")[1])
    assert "id" in redirect_url and "otp" in redirect_url


def test_verify_share_url_has_expired(session: Session) -> None:
    expired_url, _ = create_share_url(
        device_id=1, user_id=1, expiration_minutes=-1
    )  # negative timedelta makes it expired
    with pytest.raises(ExpiredShareDeviceURL):
        _ = verify_share_url(session, expired_url.split("id=")[1])


@pytest.mark.parametrize(
    "serial_number, expected_device_id",
    [
        ("DeviceSerialno0001", 1),
        ("DeviceSerialno0002", 2),
        ("DeviceSerialno0003", 3),
        ("DeviceSerialno0004", None),
        (None, None),
        (0, None),
    ],
)
def test_get_device_by_serial_number(
    session: Session, serial_number: str, expected_device_id: int
) -> None:
    device = get_device_by_serial_number(session, serial_number)
    if device:
        assert device.id == expected_device_id
    else:
        assert device == expected_device_id


def test_device_is_online(session: Session):
    device_id = 1  # is offline initially
    device = get_device(session, device_id)
    assert device.is_online == False

    fake_heartbeat = HeartBeat(
        CPU_load=0,
        MEM_load_mb=0,
        free_space_mb=0,
    )

    # sending a heartbeat will recalculate the online status in new readings
    response = update_device_heartbeat(session, device_id, fake_heartbeat)

    # as the heartbeat is recent, the device will show up online
    device = get_device(session, device_id)
    assert device.is_online == True
