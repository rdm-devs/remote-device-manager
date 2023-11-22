from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status

from src.user.constants import ErrorCode
from tests.database import app, session

client = TestClient(app)


def test_read_users(session: Session):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


def test_read_user(session: Session):
    response = client.post(
        "/users/", json={"email": "test-user@email.com", "password": "_s3cr3tp@5sw0rd_"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_id = data["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "test-user@email.com"
    assert len(data["user_groups"]) == 0


def test_read_non_existent_user(session: Session):
    user_id = 5
    response = client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_user(session: Session):
    response = client.post(
        "/users/", json={"email": "test-user@email.com", "password": "_s3cr3tp@5sw0rd_"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["email"] == "test-user@email.com"
    assert len(data["user_groups"]) == 0


def test_create_duplicated_user(session: Session):
    response = client.post(
        "/users/", json={"email": "test-user@sia.com", "password": "_s3cr3tp@5sw0rd_"}
    )  # a user with email "test-user@sia.com" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_EMAIL_TAKEN


def test_create_user_with_invalid_password(session: Session):
    response = client.post(
        "/users/", json={"email": "test-user3@sia.com", "password": ""}
    )  # a user with email "test-user@sia.com" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_INVALID_PASSWORD

    response = client.post(
        "/users/", json={"email": "test-user3@sia.com", "password": "123"}
    )  # a user with email "test-user@sia.com" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_INVALID_PASSWORD


def test_update_user(session: Session):
    # user with id=1 already exists in the session. See: tests/database.py
    user_id = 1

    # updating user's email
    response = client.patch(
        f"/users/{user_id}",
        json={"email": "test-user-updated@sia.com", "password": "1234"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test-user-updated@sia.com"


def test_update_user_invalid_password(session: Session):
    # user with id=1 already exists in the session. See: tests/database.py
    user_id = 1

    # updating user's email
    response = client.patch(
        f"/users/{user_id}",
        json={"email": "test-user-updated@sia.com", "password": "123"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_INVALID_PASSWORD


def test_update_user_with_email_taken(session: Session):
    # user with id=1 already exists in the session. See: tests/database.py
    user_id = 1

    # updating user's email
    response = client.patch(
        f"/users/{user_id}",
        json={"email": "test-user-2@sia.com", "password": "1234"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_EMAIL_TAKEN


def test_update_non_existent_user(session: Session):
    user_id = 5

    response = client.patch(
        f"/users/{user_id}",
        json={"email": "test-user-updated@sia.com", "password": "1234"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_non_existent_user_attrs(session: Session):
    user_id = 1
    response = client.patch(
        f"/users/{user_id}",
        json={
            "email": "test-user-updated@sia.com",
            "password": "1234",
            "is_admin": False,  # non existing field
            "tag": "my-cool-user-tag",  # non existing field
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_user(session: Session):
    response = client.post(
        "/users/", json={"email": "test-user-delete@sia.com", "password": "1234"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_id = data["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_user(session: Session):
    user_id = 5
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
