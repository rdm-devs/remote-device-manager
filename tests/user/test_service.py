import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tests.database import session, mock_os_data, mock_vendor_data
from src.user.exceptions import (
    UserInvalidPassword,
    UserNotFound,
    UsernameTaken,
)
from src.user.service import (
    create_user,
    get_user,
    get_users,
    delete_user,
    update_user,
    get_devices,
    get_folders,
    get_tenants,
)
from src.user.schemas import (
    UserCreate,
    UserUpdate,
)
from src.auth.utils import get_user_by_username

def test_create_user(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            username="test-user-5@sia.com",
            password="_s3cr3tp@5sw0rd_",
        ),
    )
    assert user.username == "test-user-5@sia.com"


def test_create_duplicated_user(session: Session) -> None:
    with pytest.raises(UsernameTaken):
        create_user(
            session,
            UserCreate(
                username="test-user-1@sia.com",
                password="_s3cr3tp@5sw0rd_",
            ),
        )


def test_create_user_with_invalid_password(session: Session) -> None:
    with pytest.raises(UserInvalidPassword):
        create_user(
            session,
            UserCreate(
                username="test-user-5@sia.com",
                password="123",
            ),
        )


def test_create_invalid_user(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_user(session, UserCreate())

    with pytest.raises(ValidationError):
        create_user(
            session,
            UserCreate(
                username="test-user-5@sia.com",
                password="1234",
                tag="my-custom-tag",
            ),
        )


def test_get_user(session: Session) -> None:
    user_id = 1  # created in tests/database.py
    user = get_user(session, user_id=user_id)
    assert user.username == "test-user-1@sia.com"
    assert user.hashed_password is not None
    assert user.id == 1


def test_get_user_with_invalid_id(session: Session) -> None:
    user_id = 5
    with pytest.raises(UserNotFound):
        get_user(session, user_id)


def test_get_user_by_username(session: Session) -> None:
    user = get_user_by_username(session, username="test-user-1@sia.com")
    assert user.username == "test-user-1@sia.com"
    assert user.hashed_password is not None
    assert user.id == 1


def test_get_user_with_invalid_username(session: Session) -> None:
    with pytest.raises(UserNotFound):
        get_user_by_username(session, username="test-user-5@sia.com")


def test_get_users(session: Session) -> None:
    # Four users were created in tests/database.py
    users = session.execute(get_users(session)).fetchall()
    assert len(users) == 4


def test_update_user(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            username="test-user-5@sia.com",
            password="_s3cr3tp@5sw0rd_",
        ),
    )
    db_user = get_user(session, user.id)
    prev_hashed_password = db_user.hashed_password

    user = update_user(
        session,
        db_user=db_user,
        updated_user=UserUpdate(username="test-user-5-updated@sia.com"),
    )
    assert user.username == "test-user-5-updated@sia.com"
    assert user.hashed_password is not None
    assert (
        user.hashed_password == prev_hashed_password
    )  # keeping the original password unchanged
    assert user.id == db_user.id


def test_update_user_with_invalid_attrs(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            username="test-user-5@sia.com",
            password="_s3cr3tp@5sw0rd_",
        ),
    )
    db_user = get_user(session, user.id)

    with pytest.raises(ValidationError):
        user = update_user(
            session,
            db_user=db_user,
            updated_user=UserUpdate(
                username="test-user-5@sia.com", password="1234", tag="my-custom-tag"
            ),
        )


def test_update_user_with_invalid_id(session: Session) -> None:
    db_user = get_user(session, 1)
    db_user.id = 5

    with pytest.raises(UserNotFound):
        update_user(
            session,
            db_user=db_user,
            updated_user=UserUpdate(
                username="test-user-5@sia.com", password="_s3cr3tp@5sw0rd_"
            ),
        )


def test_delete_user(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            username="test-user-delete@sia.com",
            password="_s3cr3tp@5sw0rd_",
        ),
    )
    db_user = get_user(session, user.id)

    user_id = user.id
    deleted_user_id = delete_user(session, db_user=db_user)
    assert deleted_user_id == user_id

    with pytest.raises(UserNotFound):
        get_user(session, user.id)


def test_delete_user_with_invalid_id(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            username="test-user-delete@sia.com",
            password="_s3cr3tp@5sw0rd_",
        ),
    )
    db_user = get_user(session, user.id)

    db_user.id = 6
    with pytest.raises(UserNotFound):
        delete_user(session, db_user=db_user)


def test_get_devices(session: Session) -> None:
    # user 1 is admin
    user_id = 1
    devices = session.execute(get_devices(session, user_id=user_id)).fetchall()
    assert len(devices) == 3

    # user 2 has 2 devices
    user_id = 2
    devices = session.execute(get_devices(session, user_id=user_id)).fetchall()
    assert len(devices) == 2

    # user 3 has 1 device
    user_id = 3
    devices = session.execute(get_devices(session, user_id=user_id)).fetchall()
    assert len(devices) == 1


def test_get_folders(session: Session) -> None:
    # user 1 is admin
    user_id = 1
    folders = session.execute(get_folders(session, user_id=user_id)).fetchall()
    assert len(folders) == 7

    # user 2 has 2 folders and 1 subfolder
    user_id = 2
    folders = session.execute(get_folders(session, user_id=user_id)).fetchall()
    assert len(folders) == 4

    # user 3 has 1 folder and 1 subfolder
    user_id = 3
    folders = session.execute(get_folders(session, user_id=user_id)).fetchall()
    assert len(folders) == 3


def test_get_tenants(session: Session) -> None:
    # user 1 is admin
    user_id = 1
    tenants = session.execute(get_tenants(session, user_id=user_id)).fetchall()
    assert len(tenants) == 2

    # user 2 has 1 tenant
    user_id = 2
    tenants = session.execute(get_tenants(session, user_id=user_id)).fetchall()
    assert len(tenants) == 1

    # user 3 has 1 tenant
    user_id = 3
    tenants = session.execute(get_tenants(session, user_id=user_id)).fetchall()
    assert len(tenants) == 1
