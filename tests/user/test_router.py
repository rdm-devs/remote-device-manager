from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status

from src.user.constants import ErrorCode
from tests.database import (
    app,
    session,
    mock_os_data,
    mock_vendor_data,
    client_authenticated,
)


def test_read_users(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 4


def test_read_user(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/auth/register",
        json={
            "username": "test-user@email.com",
            "password": "_s3cr3tp@5sw0rd_",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_id = data["id"]

    response = client_authenticated.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "test-user@email.com"


def test_read_non_existent_user(
    session: Session, client_authenticated: TestClient
) -> None:
    user_id = 5
    response = client_authenticated.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_user(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/auth/register",
        json={
            "username": "test-user@email.com",
            "password": "_s3cr3tp@5sw0rd_",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["username"] == "test-user@email.com"


def test_create_duplicated_user(
    session: Session, client_authenticated: TestClient
) -> None:
    response = client_authenticated.post(
        "/auth/register",
        json={
            "username": "test-user-1@sia.com",
            "password": "_s3cr3tp@5sw0rd_",
        },
    )  # a user with username "test-user@sia.com" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USERNAME_TAKEN


def test_create_user_with_invalid_password(
    session: Session, client_authenticated: TestClient
) -> None:
    response = client_authenticated.post(
        "/auth/register",
        json={
            "username": "test-user3@sia.com",
            "password": "",
        },
    )  # a user with username "test-user@sia.com" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_INVALID_PASSWORD

    response = client_authenticated.post(
        "/auth/register",
        json={
            "username": "test-user3@sia.com",
            "password": "123",
        },
    )  # a user with username "test-user@sia.com" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_INVALID_PASSWORD


def test_update_user(session: Session, client_authenticated: TestClient) -> None:
    # user with id=3 already exists in the session. See: tests/database.py
    user_id = 3
    response = client_authenticated.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    username = data["username"]

    # updating user's username
    response = client_authenticated.patch(
        f"/users/{user_id}",
        json={"username": "test-user-updated@sia.com", "tenant_ids": [1, 2]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "test-user-updated@sia.com"
    assert len(data["tenants"]) == 2


def test_update_user_invalid_password(
    session: Session, client_authenticated: TestClient
) -> None:
    # user with id=1 already exists in the session. See: tests/database.py
    user_id = 1

    # updating user's username
    response = client_authenticated.patch(
        f"/users/{user_id}",
        json={"username": "test-user-updated@sia.com", "password": "123"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_INVALID_PASSWORD


def test_update_user_with_username_taken(
    session: Session, client_authenticated: TestClient
) -> None:
    # user with id=1 already exists in the session. See: tests/database.py
    user_id = 1
    response = client_authenticated.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    username = data["username"]

    # updating user's username
    user_id = 2
    response = client_authenticated.patch(
        f"/users/{user_id}",
        json={"username": username},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USERNAME_TAKEN


def test_update_non_existent_user(
    session: Session, client_authenticated: TestClient
) -> None:
    user_id = 5

    response = client_authenticated.patch(
        f"/users/{user_id}",
        json={"username": "test-user-updated@sia.com", "password": "1234"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_non_existent_user_attrs(
    session: Session, client_authenticated: TestClient
):
    user_id = 1
    response = client_authenticated.patch(
        f"/users/{user_id}",
        json={
            "username": "test-user-updated@sia.com",
            "password": "1234",
            "is_staff": False,  # non existing field
            "favourite_color": "blue",  # non existing field
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_user(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/auth/register",
        json={
            "username": "test-user-delete@sia.com",
            "password": "12345678",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_id = data["id"]

    response = client_authenticated.delete(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_user(
    session: Session, client_authenticated: TestClient
) -> None:
    user_id = 5
    response = client_authenticated.delete(f"/users/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_devices(session: Session, client_authenticated: TestClient) -> None:
    user_id = "me"  # client_authenticated is admin
    response = client_authenticated.get(f"/users/{user_id}/devices")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 3

    user_id = 1
    response = client_authenticated.get(f"/users/{user_id}/devices")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 3

    user_id = 2
    response = client_authenticated.get(f"/users/{user_id}/devices")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 2

    user_id = 3
    response = client_authenticated.get(f"/users/{user_id}/devices")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 1

    user_id = 4
    response = client_authenticated.get(f"/users/{user_id}/devices")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 2


def test_read_folders(session: Session, client_authenticated: TestClient) -> None:
    user_id = "me"
    response = client_authenticated.get(f"/users/{user_id}/folders")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 7

    user_id = 1
    response = client_authenticated.get(f"/users/{user_id}/folders")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 7

    user_id = 2
    response = client_authenticated.get(f"/users/{user_id}/folders")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 4

    user_id = 3
    response = client_authenticated.get(f"/users/{user_id}/folders")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 3

    user_id = 4
    response = client_authenticated.get(f"/users/{user_id}/folders")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 4


def test_read_tenants(session: Session, client_authenticated: TestClient) -> None:
    user_id = "me"
    response = client_authenticated.get(f"/users/{user_id}/tenants")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 2

    user_id = 1
    response = client_authenticated.get(f"/users/{user_id}/tenants")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 2

    user_id = 2
    response = client_authenticated.get(f"/users/{user_id}/tenants")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 1

    user_id = 3
    response = client_authenticated.get(f"/users/{user_id}/tenants")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 1

    user_id = 4
    response = client_authenticated.get(f"/users/{user_id}/tenants")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 1


def test_read_tags(session: Session, client_authenticated: TestClient) -> None:
    user_id = "me"
    response = client_authenticated.get(f"/users/{user_id}/tags")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 14

    user_id = 1
    response = client_authenticated.get(f"/users/{user_id}/tags")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 14

    user_id = 2
    response = client_authenticated.get(f"/users/{user_id}/tags")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 7

    user_id = 3
    response = client_authenticated.get(f"/users/{user_id}/tags")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 5

    user_id = 4
    response = client_authenticated.get(f"/users/{user_id}/tags")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 7
