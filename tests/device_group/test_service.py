import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.tenant.exceptions import TenantNotFoundError
from tests.database import session

from src.device_group.exceptions import (
    DeviceGroupNameTakenError,
    DeviceGroupNotFoundError,
)
from src.device_group.service import (
    create_device_group,
    get_device_group,
    get_device_group_by_name,
    get_device_groups,
    delete_device_group,
    update_device_group,
)
from src.device_group.schemas import (
    DeviceGroupCreate,
    DeviceGroupUpdate,
)


def test_create_device_group(session: Session) -> None:
    device_group = create_device_group(session, DeviceGroupCreate(name="dev-group5"))
    assert device_group.name == "dev-group5"
    assert device_group.tenant_id == None


def test_create_duplicated_device(session: Session) -> None:
    with pytest.raises(DeviceGroupNameTakenError):
        create_device_group(session, DeviceGroupCreate(name="dev-group1"))


def test_create_incomplete_device(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_device_group(session, DeviceGroupCreate())


def test_create_device_group_with_invalid_tenant(session: Session) -> None:
    with pytest.raises(TenantNotFoundError):
        create_device_group(session, DeviceGroupCreate(name="dev-group5", tenant_id=5))


def test_get_device_group(session: Session) -> None:
    device_group = get_device_group(session, device_group_id=1)
    assert device_group.name == "dev-group1"
    assert device_group.tenant_id == 1


def test_get_device_group_with_invalid_id(session: Session) -> None:
    with pytest.raises(DeviceGroupNotFoundError):
        get_device_group(session, device_group_id=5)


def test_get_device_group_by_name(session: Session) -> None:
    device_group = get_device_group_by_name(session, device_group_name="dev-group1")
    assert device_group.name == "dev-group1"
    assert device_group.tenant_id == 1


def test_get_device_group_with_invalid_name(session: Session) -> None:
    with pytest.raises(DeviceGroupNotFoundError):
        get_device_group_by_name(session, device_group_name="dev-group5")


def test_get_device_groups(session: Session) -> None:
    # two device groups were created in tests/database.py
    device_groups = get_device_groups(session)
    assert len(device_groups) == 2


def test_update_device_group(session: Session) -> None:
    device_group = create_device_group(
        session, DeviceGroupCreate(name="dev-group5", tenant_id=None)
    )
    db_device_group = get_device_group(session, device_group.id)

    device_group = update_device_group(
        session,
        db_device_group=db_device_group,
        updated_device_group=DeviceGroupUpdate(name="dev-group-custom", tenant_id=1),
    )
    assert device_group.name == "dev-group-custom"
    assert device_group.tenant_id == 1


def test_update_device_group_with_invalid_tenant(session: Session) -> None:
    device_group = create_device_group(
        session, DeviceGroupCreate(name="dev-group5", tenant_id=1)
    )
    db_device_group = get_device_group(session, device_group.id)

    with pytest.raises(TenantNotFoundError):
        device_group = update_device_group(
            session,
            db_device_group=db_device_group,
            updated_device_group=DeviceGroupUpdate(
                name="dev-group-custom", tenant_id=5
            ),
        )


def test_update_device_group_with_incomplete_data(session: Session) -> None:
    device_group = create_device_group(
        session, DeviceGroupCreate(name="dev-group5", tenant_id=1)
    )
    db_device_group = get_device_group(session, device_group.id)

    with pytest.raises(ValidationError):
        device_group = update_device_group(
            session,
            db_device_group=db_device_group,
            updated_device_group=DeviceGroupUpdate(tenant_id=1, tag="my-custom-tag"),
        )


def test_update_device_group_with_invalid_id(session: Session) -> None:
    db_device_group = get_device_group(session, 1)
    db_device_group.id = 5

    with pytest.raises(DeviceGroupNotFoundError):
        update_device_group(
            session,
            db_device_group=db_device_group,
            updated_device_group=DeviceGroupUpdate(
                name="dev-group-custom", tenant_id=1
            ),
        )


def test_delete_group_device(session: Session) -> None:
    device_group = create_device_group(
        session, DeviceGroupCreate(name="dev-group5delete", tenant_id=1)
    )
    db_device_group = get_device_group(session, device_group.id)

    device_group_id = device_group.id
    deleted_device_group_id = delete_device_group(
        session, db_device_group=db_device_group
    )
    assert deleted_device_group_id == device_group_id

    with pytest.raises(DeviceGroupNotFoundError):
        get_device_group(session, device_group.id)


def test_delete_device_group_with_invalid_id(session: Session) -> None:
    device_group = create_device_group(
        session, DeviceGroupCreate(name="dev-group5delete", tenant_id=1)
    )
    db_device_group = get_device_group(session, device_group.id)

    db_device_group.id = 5
    with pytest.raises(DeviceGroupNotFoundError):
        delete_device_group(session, db_device_group=db_device_group)
