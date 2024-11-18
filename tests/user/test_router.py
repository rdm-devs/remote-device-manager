import pytest
from typing import Union
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status

from src.user.constants import ErrorCode
from tests.database import (
    app,
    session,
    mock_os_data,
    mock_vendor_data,
    client_fixture,
    client_authenticated,
    get_auth_tokens_with_user_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_status_code, n_items",
    [
        (1, status.HTTP_200_OK, 4),
        (2, status.HTTP_200_OK, 2),
        (3, status.HTTP_200_OK, 1),
        (4, status.HTTP_403_FORBIDDEN, 0),
    ],
)
async def test_read_users(
    session: Session,
    client: TestClient,
    user_id: int,
    expected_status_code: int,
    n_items: int,
) -> None:
    auth_tokens = get_auth_tokens_with_user_id(session, user_id)
    access_tokens = (await auth_tokens)["access_token"]

    response = client.get(
        f"/users",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )
    assert response.status_code == expected_status_code
    data = response.json()
    if "items" in data.keys():
        assert len(data["items"]) == n_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, read_myself_status_code, read_owner_status_code, read_admin_status_code",
    [
        (1, status.HTTP_200_OK, status.HTTP_200_OK, status.HTTP_200_OK),
        (2, status.HTTP_200_OK, status.HTTP_200_OK, status.HTTP_403_FORBIDDEN),
        (3, status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN),
        (4, status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN),
    ],
)
async def test_read_user(
    session: Session,
    client: TestClient,
    user_id: int,
    read_myself_status_code: int,
    read_owner_status_code: int,
    read_admin_status_code: int,
) -> None:
    auth_tokens = get_auth_tokens_with_user_id(session, user_id)
    access_tokens = (await auth_tokens)["access_token"]

    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )
    assert response.status_code == read_myself_status_code

    owner_user_id = 2
    response = client.get(
        f"/users/{owner_user_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )
    assert response.status_code == read_owner_status_code

    admin_user_id = 1
    response = client.get(
        f"/users/{admin_user_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )
    assert response.status_code == read_admin_status_code


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

    tenant_1 = client_authenticated.get(f"/tenants/1").json()
    tenant_2 = client_authenticated.get(f"/tenants/2").json()

    # updating user's username
    response = client_authenticated.patch(
        f"/users/{user_id}",
        json={"username": "test-user-updated@sia.com", "tenants": [tenant_1, tenant_2]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "test-user-updated@sia.com"
    assert len(data["tenants"]) == 2


@pytest.mark.parametrize(
    "user_id, body, expected_status_code",
    [
        (2, {"tags": []}, status.HTTP_200_OK),
        (2, {"tags": [], "tenant_ids": []}, status.HTTP_200_OK),
    ],
)
def test_update_user_with_empty_lists(
    session: Session,
    client_authenticated: TestClient,
    user_id: int,
    body: dict,
    expected_status_code: int,
) -> None:
    # updating user's username
    response = client_authenticated.patch(
        f"/users/{user_id}",
        json=body,
    )
    assert response.status_code == expected_status_code


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


def test_update_user_tags(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/auth/register",
        json={
            "username": "test-user-5@email.com",
            "password": "_s3cr3tp@5sw0rd_",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_id = data["id"]

    tenant_id = 1
    response = client_authenticated.get(f"/tenants/{tenant_id}/tags")
    tags_tenant_1 = response.json()["items"]
    tag_ids_tenant_1 = [tag["id"] for tag in tags_tenant_1]

    def update_tags(user_id: int):
        response = client_authenticated.patch(
            f"/users/{user_id}",
            json={
                "tags": tags_tenant_1,
            },
        )
        return response

    # the update operation will not fail even if the user has no tenant assigned
    response = update_tags(user_id)
    assert response.status_code == status.HTTP_200_OK

    # to make it work, we must assign at least one tenant to the user first
    response = client_authenticated.patch(
        f"/users/{user_id}/tenant/?tenant_id={tenant_id}"
    )
    assert response.status_code == status.HTTP_200_OK

    # now the update operation will succeed
    response = update_tags(user_id)
    assert response.status_code == status.HTTP_200_OK


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


@pytest.mark.parametrize(
    "user_id, expected_status_code, n_items",
    [
        ("me", status.HTTP_200_OK, 7),
        (1, status.HTTP_200_OK, 7),
        (2, status.HTTP_200_OK, 4),
        (3, status.HTTP_200_OK, 3),
        (4, status.HTTP_200_OK, 4),
    ],
)
def test_read_folders(
    session: Session,
    client_authenticated: TestClient,
    user_id: Union[str, int],
    expected_status_code: int,
    n_items: int,
) -> None:
    response = client_authenticated.get(f"/users/{user_id}/folders")
    assert response.status_code == expected_status_code
    assert len(response.json()["items"]) == n_items


@pytest.mark.parametrize(
    "user_id, expected_status_code, n_items",
    [
        ("me", status.HTTP_200_OK, 2),
        (1, status.HTTP_200_OK, 2),
        (2, status.HTTP_200_OK, 1),
        (3, status.HTTP_200_OK, 1),
        (4, status.HTTP_200_OK, 1),
    ],
)
def test_read_tenants(
    session: Session,
    client_authenticated: TestClient,
    user_id: Union[str, int],
    expected_status_code: int,
    n_items: int,
) -> None:
    response = client_authenticated.get(f"/users/{user_id}/tenants")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == n_items
    assert response.json()["items"][0][
        "tags"
    ]  # checking that the "tags" attribute is present


@pytest.mark.parametrize(
    "user_id, expected_status_code, n_items",
    [
        ("me", status.HTTP_200_OK, 15),
        (1, status.HTTP_200_OK, 15),
        (2, status.HTTP_200_OK, 3),
        (3, status.HTTP_200_OK, 2),
        (4, status.HTTP_200_OK, 15),
    ],
)
def test_read_tags(
    session: Session,
    client_authenticated: TestClient,
    user_id: Union[str, int],
    expected_status_code: int,
    n_items: int,
) -> None:
    response = client_authenticated.get(f"/users/{user_id}/tags")
    assert response.status_code == expected_status_code
    assert len(response.json()["assigned"]) == n_items
