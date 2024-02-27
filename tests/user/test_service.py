import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tests.database import session, mock_os_data, mock_vendor_data
from src.user.exceptions import (
    UserEmailTakenError,
    UserInvalidPasswordError,
    UserNotFoundError,
)
from src.user.service import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
    delete_user,
    update_user,
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
    with pytest.raises(UserEmailTakenError):
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
    with pytest.raises(UserInvalidPasswordError):
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
    with pytest.raises(UserNotFoundError):
        get_user(session, user_id)


def test_get_user_by_email(session: Session) -> None:
    user = get_user_by_email(session, email="test-user@sia.com")
    assert user.email == "test-user@sia.com"
    assert user.hashed_password is not None
    assert user.id == 1


def test_get_user_with_invalid_email(session: Session) -> None:
    with pytest.raises(UserNotFoundError):
        get_user_by_email(session, email="test-user-5@sia.com")


def test_get_users(session: Session) -> None:
    # Two users were created in tests/database.py
    users = get_users(session)
    assert len(users) == 2


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

    with pytest.raises(UserNotFoundError):
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

    with pytest.raises(UserNotFoundError):
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

    db_user.id = 5
    with pytest.raises(UserNotFoundError):
        delete_user(session, db_user=db_user)
