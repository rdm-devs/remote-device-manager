import pytest
from typing import Union
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.tenant.exceptions import TenantNotFound
from src.exceptions import PermissionDenied
from tests.database import session, mock_os_data, mock_vendor_data
from src.tag import exceptions, models
from src.tag.service import (
    create_tag,
    get_tag,
    get_tag_by_name,
    get_tags,
    get_available_tags,
    get_folder_available_tags,
    get_device_available_tags,
    delete_tag,
    update_tag,
    delete_tag_multi,
)
from src.tag.schemas import (
    TagCreate,
    TagUpdate,
)
from src.user import models as user_models
from src.user import service as user_service


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
            session,
            TagCreate(name="tag-test", tenant_id=None, type=models.Type.USER_CREATED),
        )


def test_create_duplicated_tag(session: Session) -> None:
    with pytest.raises(exceptions.TagNameTaken):
        create_tag(session, TagCreate(name="tag-tenant-1", tenant_id=1))

    with pytest.raises(exceptions.TagNameTaken):
        create_tag(session, TagCreate(name="Tag-Tenant-1", tenant_id=1))

    with pytest.raises(exceptions.TagNameTaken):
        create_tag(
            session,
            TagCreate(name="tag-global-1", tenant_id=None, type=models.Type.GLOBAL),
        )


def test_create_duplicated_tag_name(session: Session) -> None:
    # testing that we can create two tags with the same name but they have to have a different tenant_id.
    tenant_id = 2
    tag_name = "tag-user-2"  # already exists BUT for tenant_id=1.
    tag = create_tag(
        session,
        TagCreate(name=tag_name, tenant_id=tenant_id, type=models.Type.USER_CREATED),
    )
    assert tag.name == tag_name
    assert tag.tenant_id == tenant_id
    assert tag.type == models.Type.USER_CREATED


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
@pytest.mark.parametrize(
    "user_id, tenant_id, n_items",
    [(1, None, 15), (1, 1, 3), (3, 2, 2)],
)
async def test_get_tags(
    session: Session, user_id: int, tenant_id: Union[int, None], n_items: int
) -> None:
    user = session.scalars(
        select(user_models.User).where(user_models.User.id == user_id)
    ).first()
    tags = await get_tags(session, auth_user=user, user_id=user_id, tenant_id=tenant_id)
    assert len(tags) == n_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, folder_id, n_items",
    [(1, 1, 1), (2, 1, 1), (3, 2, 1)],
)
async def test_get_folder_tags(
    session: Session, user_id: int, folder_id: int, n_items: int
) -> None:
    user = session.scalars(
        select(user_models.User).where(user_models.User.id == user_id)
    ).first()
    tags = await get_tags(session, auth_user=user, user_id=user_id, folder_id=folder_id)
    assert len(tags) == n_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, device_id, n_items",
    [(1, 1, 2), (1, 2, 1), (1, 3, 1), (2, 1, 2), (2, 2, 1), (3, 3, 1)],
)
async def test_get_device_tags(
    session: Session, user_id: int, device_id: int, n_items: int
) -> None:
    user = session.scalars(
        select(user_models.User).where(user_models.User.id == user_id)
    ).first()
    tags = await get_tags(session, auth_user=user, user_id=user_id, device_id=device_id)
    assert len(tags) == n_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, name, n_items",
    [
        (1, "tag", 15),
        (1, "tenant", 11),
        (1, "dev", 1),
        (2, "tenant-1", 1),
        (2, "user-2", 1),
        (3, "global", 0),
    ],
)
async def test_get_tags_by_name(
    session: Session, user_id: int, name: str, n_items: int
) -> None:
    user = session.scalars(
        select(user_models.User).where(user_models.User.id == user_id)
    ).first()
    tags = await get_tags(session, auth_user=user, user_id=user_id, name=name)
    assert len(tags) == n_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, tenant_id",
    [(3, 1), (2, 2)],
)
async def test_get_tags_forbidden_tenant(
    session: Session, user_id: int, tenant_id: int
) -> None:
    with pytest.raises(PermissionDenied):
        user = session.scalars(
            select(user_models.User).where(user_models.User.id == user_id)
        ).first()
        tags = await get_tags(
            session, auth_user=user, user_id=user_id, tenant_id=tenant_id
        )


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, user_id, tenant_id, folder_id, device_id, n_expected_items",
    [
        # tags available for user.id = 1
        (None, 1, None, None, None, 15),
        # tags available for user.id = 2
        (None, 2, None, None, None, 9),
        # tags available for user.id = 3
        (None, 3, None, None, None, 7),
        # tags available for tenant.id=1, owned by user.id = 1
        (None, 1, 1, None, None, 9),
        # tags available for folder.id=3, owned by user.id = 1
        (None, 1, None, 3, None, 5),
        # tags available for folder.id=6, owned by user.id = 1
        (None, 1, None, 6, None, 4),
        # tags available for device.id=2, owned by user.id = 1
        (None, 1, None, None, 2, 4),
        # tags available for device.id=1, owned by user.id = 1
        (None, 1, None, None, 1, 5),
        # tags available with name containing "folder1", owned by user.id = 1
        ("folder1", 1, None, None, None, 2),
        # tags available for folder.id=3 with name containing "folder1", owned by user.id = 1
        ("folder1", 1, None, 3, None, 1),
        # tags available with name containing "folder3", owned by user.id = 1
        ("folder3", 1, None, None, None, 1),
        # tags available for folder.id=3, owned by user.id = 3 -> should fail w/PermissionDenied
        (None, 3, None, 3, None, None),
        # tags available for device.id=2, owned by user.id = 3 -> should fail w/PermissionDenied
        (None, 3, None, None, 2, None),
        # tags available for device.id=1 with name containing "dev-1", owned by user.id = 1
        ("dev-1", 1, None, None, 1, 1),
    ],
)
async def test_get_available_tags(
    session: Session,
    name: Union[None, str],
    user_id: Union[None, int],
    tenant_id: Union[None, int],
    folder_id: Union[None, int],
    device_id: Union[None, int],
    n_expected_items: Union[None, int],
) -> None:
    async def get_tags():
        user = session.scalars(
            select(user_models.User).where(user_models.User.id == user_id)
        ).first()
        tags = await get_available_tags(
            session, user, user_id, name, tenant_id, folder_id, device_id
        )
        assert len(tags) == n_expected_items

    if not n_expected_items:
        with pytest.raises(PermissionDenied):
            await get_tags()
    else:
        await get_tags()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "folder_id, n_expected_items",
    [
        (1, 4),
        (2, 4),
        (3, 5),
        (4, 4),
        (5, 5),
        (6, 4),
        (7, 4),
    ],
)
async def test_get_folder_available_tags(
    session: Session, folder_id: int, n_expected_items: int
):
    tags = select(models.Tag)
    available_tags_query = get_folder_available_tags(session, folder_id, tags)
    available_tags = session.scalars(available_tags_query).all()
    assert len(available_tags) == n_expected_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "device_id, n_expected_items",
    [
        (1, 5),
        (2, 4),
        (3, 5),
    ],
)
async def test_get_device_available_tags(
    session: Session, device_id: int, n_expected_items: int
):
    tags = select(models.Tag)
    available_tags_query = get_device_available_tags(session, device_id, tags)
    available_tags = session.scalars(available_tags_query).all()
    assert len(available_tags) == n_expected_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, n_expected_tags_deleted",
    [
        (1, 5),
        (2, 0),
        (3, 0),
        (4, 0),
    ],
)
async def test_delete_tag_multi(
    session: Session, user_id: int, n_expected_tags_deleted: int
) -> None:
    user = user_service.get_user(session, user_id)
    tags = await get_tags(session, user, user.id)
    tag_ids = list(map(lambda t: t.id, tags))

    deleted_tag_ids, deleted_rows = delete_tag_multi(
        session, user=user, tag_ids=tag_ids
    )
    assert deleted_tag_ids == tag_ids
    assert deleted_rows == n_expected_tags_deleted
