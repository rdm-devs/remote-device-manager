import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tests.database import session, mock_os_data, mock_vendor_data
from src.user.exceptions import (
    UserEmailTaken,
    UserInvalidPassword,
    UserNotFound,
)
from src.user.service import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
    delete_user,
    update_user,
    get_devices,
    get_folders,
    get_tenants
)
from src.user.schemas import (
    UserCreate,
    UserUpdate,
)


def test_create_user(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(email="test-user-5@sia.com", username="test-user-5", password="_s3cr3tp@5sw0rd_", role_id=1),
    )
    assert user.email == "test-user-5@sia.com"


def test_create_duplicated_user(session: Session) -> None:
    with pytest.raises(UserEmailTaken):
        create_user(
            session,
            UserCreate(
                email="test-user@sia.com",
                username="test-user-5",
                password="_s3cr3tp@5sw0rd_",
                role_id=1,
            ),
        )


def test_create_user_with_invalid_password(session: Session) -> None:
    with pytest.raises(UserInvalidPassword):
        create_user(
            session,
            UserCreate(
                email="test-user-5@sia.com",
                username="test-user-5",
                password="123",
                role_id=1,
            ),
        )


def test_create_invalid_user(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_user(session, UserCreate())

    with pytest.raises(ValidationError):
        create_user(
            session,
            UserCreate(
                email="test-user-5@sia.com",
                username="test-user-5",
                password="1234",
                tag="my-custom-tag",
            ),
        )


def test_get_user(session: Session) -> None:
    user_id = 1  # created in tests/database.py
    user = get_user(session, user_id=user_id)
    assert user.email == "test-user@sia.com"
    assert user.hashed_password is not None
    assert user.id == 1


def test_get_user_with_invalid_id(session: Session) -> None:
    user_id = 5
    with pytest.raises(UserNotFound):
        get_user(session, user_id)


def test_get_user_by_email(session: Session) -> None:
    user = get_user_by_email(session, email="test-user@sia.com")
    assert user.email == "test-user@sia.com"
    assert user.hashed_password is not None
    assert user.id == 1


def test_get_user_with_invalid_email(session: Session) -> None:
    with pytest.raises(UserNotFound):
        get_user_by_email(session, email="test-user-5@sia.com")


def test_get_users(session: Session) -> None:
    # Two users were created in tests/database.py
    query_users = get_users(session)
    users = query_users.all() # need to resolve query as in the route we use it for pagination but do not resolve it ourselves
    assert len(users) == 4


def test_update_user(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            email="test-user-5@sia.com",
            username="test-user-5",
            password="_s3cr3tp@5sw0rd_",
            role_id=1,
        ),
    )
    db_user = get_user(session, user.id)
    prev_hashed_password = db_user.hashed_password

    user = update_user(
        session,
        db_user=db_user,
        updated_user=UserUpdate(email="test-user-5-updated@sia.com"),
    )
    assert user.email == "test-user-5-updated@sia.com"
    assert user.hashed_password is not None
    assert (
        user.hashed_password == prev_hashed_password
    )  # keeping the original password unchanged
    assert user.id == db_user.id


def test_update_user_with_invalid_attrs(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            email="test-user-5@sia.com",
            username="test-user-5",
            password="_s3cr3tp@5sw0rd_",
            role_id=1,
        ),
    )
    db_user = get_user(session, user.id)

    with pytest.raises(ValidationError):
        user = update_user(
            session,
            db_user=db_user,
            updated_user=UserUpdate(
                email="test-user-5@sia.com", password="1234", tag="my-custom-tag"
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
                email="test-user-5@sia.com", password="_s3cr3tp@5sw0rd_"
            ),
        )


def test_delete_user(session: Session) -> None:
    user = create_user(
        session,
        UserCreate(
            email="test-user-delete@sia.com",
            username="test-user-5",
            password="_s3cr3tp@5sw0rd_",
            role_id=1,
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
            email="test-user-delete@sia.com",
            username="test-user-5",
            password="_s3cr3tp@5sw0rd_",
            role_id=1,
        ),
    )
    db_user = get_user(session, user.id)

    db_user.id = 6
    with pytest.raises(UserNotFound):
        delete_user(session, db_user=db_user)


def test_get_devices(session: Session) -> None:
    # user 1 is admin
    user_id = 1
    devices = get_devices(session, user_id=user_id).all()
    assert len(devices) == 3

    # user 2 has 2 devices
    user_id = 2
    devices = get_devices(session, user_id=user_id).all()
    assert len(devices) == 2

    # user 3 has 1 device
    user_id = 3
    devices = get_devices(session, user_id=user_id).all()
    assert len(devices) == 1


def test_get_folders(session: Session) -> None:
    # user 1 is admin
    user_id = 1
    folders = get_folders(session, user_id=user_id).all()
    assert len(folders) == 5

    # user 2 has 2 folders and 1 subfolder
    user_id = 2
    folders = get_folders(session, user_id=user_id).all()
    assert len(folders) == 3

    # user 3 has 1 folder and 1 subfolder
    user_id = 3
    folders = get_folders(session, user_id=user_id).all()
    assert len(folders) == 2


def test_get_tenants(session: Session) -> None:
    # user 1 is admin
    user_id = 1
    tenants = get_tenants(session, user_id=user_id).all()
    assert len(tenants) == 2

    # user 2 has 1 tenant
    user_id = 2
    tenants = get_tenants(session, user_id=user_id).all()
    assert len(tenants) == 1

    # user 3 has 1 tenant
    user_id = 3
    tenants = get_tenants(session, user_id=user_id).all()
    assert len(tenants) == 1
