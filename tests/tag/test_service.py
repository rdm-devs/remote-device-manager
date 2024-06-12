import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.tenant.exceptions import TenantNotFound
from tests.database import session, mock_os_data, mock_vendor_data
from src.tag import exceptions, models
from src.tag.service import (
    create_tag,
    get_tag,
    get_tag_by_name,
    get_tags,
    delete_tag,
    update_tag,
)
from src.tag.schemas import (
    TagCreate,
    TagUpdate,
)
from src.user import models as user_models


@pytest.mark.parametrize(
    "tag_name, tenant_id, expected_tenant_id, type",
    [
        ("tag-test", None, None, models.Type.GLOBAL),
        ("tag-test", 1, None, models.Type.GLOBAL),
        ("tag-test", 1, 1, models.Type.USER_CREATED),
    ],
)
def test_create_tag(
    session: Session,
    tag_name: str,
    tenant_id: int,
    expected_tenant_id: int,
    type: models.Type,
) -> None:
    tag = create_tag(session, TagCreate(name=tag_name, tenant_id=tenant_id, type=type))
    assert tag.name == tag_name
    assert tag.tenant_id == expected_tenant_id
    assert tag.type == type


def test_create_tag_invalid_tenant_id_user_created(session: Session) -> None:
    with pytest.raises(exceptions.TagNotFound):
        tag = create_tag(
            session, TagCreate(name="tag-test", tenant_id=None, type=models.Type.USER_CREATED)
        )


def test_create_duplicated_tag(session: Session) -> None:
    with pytest.raises(exceptions.TagNameTaken):
        create_tag(session, TagCreate(name="tag-tenant-1", tenant_id=1))


def test_create_incomplete_Tag(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_tag(session, TagCreate())


def test_create_tag_with_invalid_tenant(session: Session) -> None:
    with pytest.raises(TenantNotFound):
        create_tag(session, TagCreate(name="tag-test", tenant_id=5))


def test_get_tag(session: Session) -> None:
    tag = get_tag(session, tag_id=1)
    assert tag.name == "tenant-tenant1-tag"
    assert tag.tenant_id == 1


def test_get_tag_with_invalid_id(session: Session) -> None:
    tag_id = 20
    with pytest.raises(exceptions.TagNotFound):
        get_tag(session, tag_id=tag_id)


def test_get_tag_by_name(session: Session) -> None:
    # the following tag was defined in tests/database.py
    tag = get_tag_by_name(session, tag_name="tag-tenant-1")
    assert tag.name == "tag-tenant-1"
    assert tag.tenant_id == 1


def test_get_tag_with_invalid_name(session: Session) -> None:
    with pytest.raises(exceptions.TagNotFound):
        get_tag_by_name(session, tag_name="tag-test")

@pytest.mark.asyncio
async def test_get_tags(session: Session) -> None:
    # eight tags were created in tests/database.py
    tags = session.execute(await get_tags(session, user_id=1)).fetchall()
    assert len(tags) == 15


def test_update_tag(session: Session) -> None:
    tag = create_tag(session, TagCreate(name="tag-test", tenant_id=1))
    db_tag = get_tag(session, tag.id)

    tag = update_tag(
        session,
        db_tag=db_tag,
        updated_tag=TagUpdate(name="tag-test-custom"),
    )
    assert tag.name == "tag-test-custom"
    assert tag.tenant_id == 1


def test_update_tag_with_invalid_tenant(session: Session) -> None:
    tag = create_tag(session, TagCreate(name="tag-test", tenant_id=1))
    db_tag = get_tag(session, tag.id)

    tenant_id = 20
    with pytest.raises(TenantNotFound):
        tag = update_tag(
            session,
            db_tag=db_tag,
            updated_tag=TagUpdate(name="tag-test-custom", tenant_id=tenant_id),
        )


def test_update_tag_with_invalid_id(session: Session) -> None:
    db_tag = get_tag(session, 1)
    db_tag.id = 20

    with pytest.raises(exceptions.TagNotFound):
        update_tag(
            session,
            db_tag=db_tag,
            updated_tag=TagUpdate(name="tag-test-custom"),
        )


def test_delete_tag(session: Session) -> None:
    tag = create_tag(session, TagCreate(name="tag-test-delete", tenant_id=1))
    db_tag = get_tag(session, tag.id)

    deleted_tag_id = delete_tag(session, db_tag=db_tag)
    assert deleted_tag_id == tag.id

    with pytest.raises(exceptions.TagNotFound):
        get_tag(session, tag.id)


def test_delete_tag_with_invalid_id(session: Session) -> None:
    db_tag = get_tag(session, 1)

    db_tag.id = 20  # this id must not exist
    with pytest.raises(exceptions.TagNotFound):
        delete_tag(session, db_tag=db_tag)
