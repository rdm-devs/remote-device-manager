import os
import pytest
from dotenv import load_dotenv
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Union
from tests.database import session, mock_os_data, mock_vendor_data

from src.tenant.exceptions import (
    TenantNameTaken,
    TenantNotFound,
    TenantCannotBeDeleted,
)
from src.tenant.service import (
    create_tenant,
    get_tenant,
    get_tenant_by_name,
    get_tenants,
    delete_tenant,
    update_tenant,
    get_tenant_settings,
    create_default_tenant_settings,
    create_tenant_settings,
    update_tenant_settings,
)
from src.tenant.schemas import TenantCreate, TenantUpdate, TenantSettings
from src.user import models as user_models
from src.tag.schemas import TagCreate
from src.tag.service import create_tag
from src.tag.models import entities_and_tags_table, Tag, Type

load_dotenv()


def test_create_tenant(session: Session) -> None:
    tenant5 = create_tenant(session, TenantCreate(name="tenant5"))
    assert tenant5.name == "tenant5"
    assert len(tenant5.folders) == 1
    # when creating a tenant we create a root folder for it, each having their automatic tag.
    assert len(tenant5.tags) == 1
    assert len(tenant5.tags_for_tenant) == 2

    tag = create_tag(
        session, TagCreate(name="custom-new-tag", tenant_id=None, type=Type.GLOBAL)
    )
    tenant6 = create_tenant(session, TenantCreate(name="tenant6", tags=[tag]))
    assert tenant6.name == "tenant6"
    assert len(tenant6.folders) == 1
    # similar to tenant5, tenant6 will have 2 tags + the one that we passed on creation.
    assert len(tenant6.tags) == 2
    assert len(tenant6.tags_for_tenant) == 2


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
    tenant_name = "tenant5"
    tenant = create_tenant(session, TenantCreate(name=tenant_name))
    db_tenant = get_tenant(session, tenant.id)
    original_tags = tenant.tags

    # attempting to update tenant tags with tags from another tenant
    tenant_2 = get_tenant(session, 2)
    tags = [*tenant.tags, *tenant_2.tags]
    tenant = update_tenant(
        session,
        db_tenant=db_tenant,
        updated_tenant=TenantUpdate(name=tenant_name, tags=tags),
    )
    assert tenant.name == tenant_name
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


def test_update_tenant_with_empty_tag_list(session: Session) -> None:
    tenant_id = 1
    tenant = get_tenant(session, tenant_id)
    original_tags = tenant.tags
    user_created_tags = list(
        filter(lambda t: t.type == Type.USER_CREATED, original_tags)
    )

    tenant = update_tenant(
        session, db_tenant=tenant, updated_tenant=TenantUpdate(tags=[])
    )
    assert all(t not in tenant.tags for t in user_created_tags)


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


@pytest.mark.parametrize(
    "tenant_id, exception",
    [
        (1, None),
        (2, None),
        (3, TenantNotFound),
        (99, TenantNotFound),
    ],
)
def test_read_tenant_settings(
    session: Session, tenant_id: int, exception: Union[None, TenantNotFound]
) -> None:
    expected_result = TenantSettings(heartbeat_s=int(os.getenv("HEARTBEAT_S")))
    if exception:
        with pytest.raises(exception):
            settings = get_tenant_settings(session, tenant_id)
    else:
        settings = get_tenant_settings(session, tenant_id)
        assert settings.heartbeat_s == expected_result.heartbeat_s


@pytest.mark.parametrize(
    "tenant_id, tenant_settings_before, tenant_settings_after, exception",
    [
        (1, {"heartbeat_s": 6}, {"heartbeat_s": 20}, None),
        (1, {"heartbeat_s": 6}, {"heartbeat_s": -10}, ValidationError),
        (99, None, None, TenantNotFound),
    ],
)
def test_update_tenant_settings(
    session: Session,
    tenant_id: int,
    tenant_settings_before: dict,
    tenant_settings_after: dict,
    exception: Union[None, TenantNotFound, ValidationError],
) -> None:
    if exception:
        with pytest.raises(exception):
            settings = get_tenant_settings(session, tenant_id)

            new_settings = update_tenant_settings(
                session, tenant_id, TenantSettings(**tenant_settings_after)
            )

    else:
        settings = get_tenant_settings(session, tenant_id)
        assert settings.heartbeat_s == tenant_settings_before["heartbeat_s"]

        new_settings = update_tenant_settings(
            session, tenant_id, TenantSettings(**tenant_settings_after)
        )
        assert new_settings.heartbeat_s == tenant_settings_after["heartbeat_s"]
