import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.user_group.router import get_users_from_user_group
from tests.database import session
from src.user_group.exceptions import (
    UserGroupNameTakenError,
    UserGroupInvalidNameError,
    UserGroupNotFoundError,
)
from src.device_group.exceptions import DeviceGroupNotFoundError
from src.user_group.service import (
    create_user_group,
    get_user_group,
    get_user_group_by_name,
    get_user_groups,
    delete_user_group,
    update_user_group,
    add_users,
    delete_users,
)
from src.user_group.schemas import (
    UserGroupCreate,
    UserGroupUpdate,
)
from src.user.service import get_users


def test_create_user_group(session: Session) -> None:
    user_group = create_user_group(
        session, UserGroupCreate(name="user-group-5", device_group_id=1)
    )
    assert user_group.name == "user-group-5"
    assert user_group.device_group_id == 1
    assert len(user_group.users) == 0


def test_create_duplicated_user_group(session: Session) -> None:
    with pytest.raises(UserGroupNameTakenError):
        create_user_group(
            session, UserGroupCreate(name="user-group1", device_group_id=1)
        )


def test_create_user_group_with_invalid_name(session: Session) -> None:
    with pytest.raises(UserGroupInvalidNameError):
        create_user_group(session, UserGroupCreate(name="", device_group_id=1))


def test_create_user_group_with_invalid_device_group_id(session: Session) -> None:
    with pytest.raises(DeviceGroupNotFoundError):
        create_user_group(
            session, UserGroupCreate(name="user-group-5", device_group_id=-1)
        )


def test_create_invalid_user_group(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_user_group(session, UserGroupCreate())

    with pytest.raises(ValidationError):
        create_user_group(
            session,
            UserGroupCreate(
                name="user-group-5", device_group_id=1, tag="my-custom-tag"
            ),
        )


def test_get_user_group(session: Session) -> None:
    user_group_id = 1  # created in tests/database.py
    user_group = get_user_group(session, user_group_id=user_group_id)
    assert user_group.id == 1
    assert user_group.name == "user-group1"
    assert user_group.device_group_id is not None
    assert len(user_group.users) == 2


def test_get_user_group_with_invalid_id(session: Session) -> None:
    user_group_id = 5
    with pytest.raises(UserGroupNotFoundError):
        get_user_group(session, user_group_id)


def test_get_user_group_by_name(session: Session) -> None:
    user_group = get_user_group_by_name(session, name="user-group1")
    assert user_group.id == 1
    assert user_group.name == "user-group1"
    assert user_group.device_group_id == 1
    assert len(user_group.users) == 2


def test_get_user_group_with_invalid_name(session: Session) -> None:
    with pytest.raises(UserGroupNotFoundError):
        get_user_group_by_name(session, name="user-group-5")


def test_get_user_groups(session: Session) -> None:
    # Two user_groups were created in tests/database.py
    user_groups = get_user_groups(session)
    assert len(user_groups) == 2


def test_update_user_group(session: Session) -> None:
    user_group = create_user_group(
        session, UserGroupCreate(name="user-group-5", device_group_id=1)
    )
    db_user_group = get_user_group(session, user_group.id)

    user_group = update_user_group(
        session,
        db_user_group=db_user_group,
        updated_user_group=UserGroupUpdate(name="user-group-5-updated"),
    )
    assert user_group.id == db_user_group.id
    assert user_group.name == "user-group-5-updated"
    assert user_group.device_group_id == 1
    assert len(user_group.users) == 0


def test_update_user_group_with_invalid_attrs(session: Session) -> None:
    user_group = create_user_group(
        session, UserGroupCreate(name="user-group-5", device_group_id=1)
    )
    db_user_group = get_user_group(session, user_group.id)

    with pytest.raises(ValidationError):
        user_group = update_user_group(
            session,
            db_user_group=db_user_group,
            updated_user_group=UserGroupUpdate(
                name="user-group-5-updated", device_group_id=1, tag="my-custom-tag"
            ),
        )


def test_update_user_group_with_incomplete_data(session: Session) -> None:
    user_group = create_user_group(
        session, UserGroupCreate(name="user-group-5", device_group_id=1)
    )
    db_user_group = get_user_group(session, user_group.id)

    with pytest.raises(ValidationError):
        user_group = update_user_group(
            session,
            db_user_group=db_user_group,
            updated_user_group=UserGroupUpdate(),
        )


def test_update_user_group_with_invalid_id(session: Session) -> None:
    db_user_group = get_user_group(session, user_group_id=1)

    db_user_group.id = 5
    with pytest.raises(UserGroupNotFoundError):
        update_user_group(
            session,
            db_user_group=db_user_group,
            updated_user_group=UserGroupUpdate(name="user-group-5-updated"),
        )


def test_delete_user_group(session: Session) -> None:
    user_group = create_user_group(
        session, UserGroupCreate(name="user-group-delete", device_group_id=1)
    )
    db_user_group = get_user_group(session, user_group.id)

    user_group_id = user_group.id
    deleted_user_group_id = delete_user_group(session, db_user_group=db_user_group)
    assert deleted_user_group_id == user_group_id

    with pytest.raises(UserGroupNotFoundError):
        get_user_group(session, user_group.id)


def test_delete_user_group_with_invalid_id(session: Session) -> None:
    user_group = create_user_group(
        session, UserGroupCreate(name="user-group-delete", device_group_id=1)
    )
    db_user_group = get_user_group(session, user_group.id)

    db_user_group.id = 5
    with pytest.raises(UserGroupNotFoundError):
        delete_user_group(session, db_user_group=db_user_group)


def test_add_users(session: Session) -> None:
    user = create_user_group(
        session, UserGroupCreate(name="user-group-5", device_group_id=1)
    )
    db_user_group = get_user_group(session, 2)
    assert len(db_user_group.users) == 0

    db_users = get_users(session)

    updated_user_group = add_users(session, db_user_group, db_users)
    assert (
        len(updated_user_group.users) == 3
    )  # there are 3 users in the session, see tests/database.py


def test_delete_users(session: Session) -> None:
    db_user_group = get_user_group(session, 1)
    assert len(db_user_group.users) == 2

    # users_ids = [u.id for u in db_user_group.users]
    updated_user_group = delete_users(session, db_user_group, db_user_group.users)
    assert len(updated_user_group.users) == 0


def test_get_users(session: Session) -> None:
    users = get_users_from_user_group(1, session)
    assert len(users) == 2
