import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from tests.database import session, mock_os_data, mock_vendor_data

from src.tenant.exceptions import (
    TenantNameTakenError,
    TenantNotFoundError,
)
from src.tenant.service import (
    create_tenant,
    get_tenant,
    get_tenant_by_name,
    get_tenants,
    delete_tenant,
    update_tenant,
)
from src.tenant.schemas import (
    TenantCreate,
    TenantUpdate,
)


def test_create_tenant(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5"))
    assert tenant.name == "tenant5"
    assert len(tenant.folders) == 0


def test_create_duplicated_tenant(session: Session) -> None:
    with pytest.raises(TenantNameTakenError):
        create_tenant(session, TenantCreate(name="tenant1"))


def test_create_incomplete_tenant(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_tenant(session, TenantCreate())


def test_create_tenant_with_folder(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_tenant(session, TenantCreate(name="tenant5", folders=[]))


def test_get_tenant(session: Session) -> None:
    tenant = get_tenant(session, tenant_id=1)
    assert tenant.name == "tenant1"
    assert tenant.id == 1


def test_get_tenant_with_invalid_id(session: Session) -> None:
    tenant_id = 5
    with pytest.raises(TenantNotFoundError):
        get_tenant(session, tenant_id)


def test_get_tenant_by_name(session: Session) -> None:
    tenant = get_tenant_by_name(session, tenant_name="tenant1")
    assert tenant.name == "tenant1"
    assert tenant.id == 1
    assert len(tenant.folders) == 3  # see tests/database.py


def test_get_tenant_with_invalid_name(session: Session) -> None:
    with pytest.raises(TenantNotFoundError):
        tenant = get_tenant_by_name(session, tenant_name="tenant5")


def test_get_tenants(session: Session) -> None:
    # a tenant was created in tests/database.py
    tenants = get_tenants(session)
    assert len(tenants) == 2


def test_update_tenant(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5"))
    db_tenant = get_tenant(session, tenant.id)

    tenant = update_tenant(
        session,
        db_tenant=db_tenant,
        updated_tenant=TenantUpdate(name="tenant-custom"),
    )
    assert tenant.name == "tenant-custom"
    assert tenant.id == db_tenant.id


def test_update_tenant_with_invalid_attrs(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5"))
    db_tenant = get_tenant(session, tenant.id)

    with pytest.raises(ValidationError):
        tenant = update_tenant(
            session,
            db_tenant=db_tenant,
            updated_tenant=TenantUpdate(name="tenant-custom", tag="my-custom-tag"),
        )


def test_update_tenant_with_incomplete_data(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5"))
    db_tenant = get_tenant(session, tenant.id)

    with pytest.raises(ValidationError):
        tenant = update_tenant(
            session,
            db_tenant=db_tenant,
            updated_tenant=TenantUpdate(),
        )


def test_update_tenant_with_invalid_id(session: Session) -> None:
    db_tenant = get_tenant(session, 1)
    db_tenant.id = 5

    with pytest.raises(TenantNotFoundError):
        update_tenant(
            session,
            db_tenant=db_tenant,
            updated_tenant=TenantUpdate(name="tenant-custom"),
        )


def test_delete_tenant(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5delete"))
    db_tenant = get_tenant(session, tenant.id)

    tenant_id = tenant.id
    deleted_tenant_id = delete_tenant(session, db_tenant=db_tenant)
    assert deleted_tenant_id == tenant_id

    with pytest.raises(TenantNotFoundError):
        get_tenant(session, tenant.id)


def test_delete_tenant_with_invalid_id(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5delete"))
    db_tenant = get_tenant(session, tenant.id)

    db_tenant.id = 5
    with pytest.raises(TenantNotFoundError):
        delete_tenant(session, db_tenant=db_tenant)
