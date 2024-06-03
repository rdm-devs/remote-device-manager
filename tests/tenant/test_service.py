import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from tests.database import session, mock_os_data, mock_vendor_data

from src.tenant.exceptions import TenantNameTaken, TenantNotFound, TenantCannotBeDeleted
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
from src.user import models as user_models
from src.tag.schemas import TagCreate
from src.tag.service import create_tag


def test_create_tenant(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5"))
    assert tenant.name == "tenant5"
    assert len(tenant.folders) == 1


def test_create_duplicated_tenant(session: Session) -> None:
    with pytest.raises(TenantNameTaken):
        create_tenant(session, TenantCreate(name="tenant1"))


def test_create_incomplete_tenant(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_tenant(session, TenantCreate())


def test_get_tenant(session: Session) -> None:
    tenant = get_tenant(session, tenant_id=1)
    assert tenant.name == "tenant1"
    assert tenant.id == 1


def test_get_tenant_with_invalid_id(session: Session) -> None:
    tenant_id = 5
    with pytest.raises(TenantNotFound):
        get_tenant(session, tenant_id)


def test_get_tenant_by_name(session: Session) -> None:
    tenant = get_tenant_by_name(session, tenant_name="tenant1")
    assert tenant.name == "tenant1"
    assert tenant.id == 1
    assert len(tenant.folders) == 4  # see tests/database.py


def test_get_tenant_with_invalid_name(session: Session) -> None:
    with pytest.raises(TenantNotFound):
        tenant = get_tenant_by_name(session, tenant_name="tenant5")


def test_get_tenants(session: Session) -> None:
    # two tenants were created in tests/database.py
    admin = (
        session.query(user_models.User).filter(user_models.User.role_id == 1).first()
    )
    tenants = session.scalars(get_tenants(session, admin.id)).all()
    assert len(tenants) == 2  # admin can access them all

    owner_2 = session.query(user_models.User).filter(user_models.User.id == 2).first()
    tenants = session.scalars(get_tenants(session, owner_2.id)).all()
    assert len(tenants) == 1
    assert tenants[0].id == 1  # each owner has a different tenant

    owner_3 = session.query(user_models.User).filter(user_models.User.id == 3).first()
    tenants = session.scalars(get_tenants(session, owner_3.id)).all()
    assert len(tenants) == 1
    assert tenants[0].id == 2

    user = session.query(user_models.User).filter(user_models.User.id == 4).first()
    tenants = session.scalars(get_tenants(session, user.id)).all()
    assert len(tenants) == 1


def test_update_tenant(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5"))
    db_tenant = get_tenant(session, tenant.id)
    original_tags = tenant.tags

    # attempting to update tenant tags with tags from another tenant
    tenant_2 = get_tenant(session, 2)
    tags = [*tenant.tags, *tenant_2.tags]
    tenant = update_tenant(
        session,
        db_tenant=db_tenant,
        updated_tenant=TenantUpdate(name="tenant-custom", tags=tags),
    )
    assert tenant.name == "tenant-custom"
    assert tenant.id == db_tenant.id
    assert all(t in tenant.tags for t in original_tags)
    assert all(
        t not in tenant.tags for t in tenant_2.tags
    )  # invalid tags were filtered

    # adding new tags to the tenant
    tag_1 = create_tag(session, TagCreate(name="custom-new-tag-1", tenant_id=tenant.id))
    tag_2 = create_tag(session, TagCreate(name="custom-new-tag-2", tenant_id=tenant.id))

    new_tags = [*tenant.tags, tag_1, tag_2]  # combining new tags with existing ones
    tenant = update_tenant(
        session,
        db_tenant=tenant,
        updated_tenant=TenantUpdate(tags=new_tags),
    )
    assert all(t in tenant.tags for t in new_tags)


def test_update_tenant_with_invalid_id(session: Session) -> None:
    db_tenant = get_tenant(session, 1)
    db_tenant.id = 5

    with pytest.raises(TenantNotFound):
        update_tenant(
            session,
            db_tenant=db_tenant,
            updated_tenant=TenantUpdate(name="tenant-custom"),
        )


def test_delete_tenant(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5delete"))
    db_tenant = get_tenant(session, tenant.id)

    with pytest.raises(TenantCannotBeDeleted):
        deleted_tenant_id = delete_tenant(session, db_tenant=db_tenant)
        assert deleted_tenant_id == tenant.id


def test_delete_tenant_with_invalid_id(session: Session) -> None:
    tenant = create_tenant(session, TenantCreate(name="tenant5delete"))
    db_tenant = get_tenant(session, tenant.id)

    db_tenant.id = 5
    with pytest.raises(TenantNotFound):
        delete_tenant(session, db_tenant=db_tenant)
