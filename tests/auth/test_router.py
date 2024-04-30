import time
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.constants import ErrorCode
from tests.database import (
    app,
    session,
    client_fixture,
    mock_os_data,
    mock_vendor_data,
    admin_auth_tokens,
    owner_2_auth_tokens,
    owner_3_auth_tokens,
    user_auth_tokens,
)


def test_login(client: TestClient) -> None:
    response = client.post(
        "/auth/token", data={"username": "test-user-1", "password": "_s3cr3tp@5sw0rd_"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


@pytest.mark.asyncio
async def test_logout(client: TestClient, admin_auth_tokens: dict) -> None:
    # then we keep the refresh_token in order to logout
    refresh_token = (await admin_auth_tokens)["refresh_token"]
    response = client.delete("/auth/token", params={"refresh_token": refresh_token})
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["msg"]


@pytest.mark.asyncio
async def test_refresh_token(client: TestClient, admin_auth_tokens: dict) -> None:
    # keeping the old access and refresh tokens to compare them with the refresh token endpoint result
    tokens = await admin_auth_tokens
    old_access_token = tokens["access_token"]
    old_refresh_token = tokens["refresh_token"]

    time.sleep(1)
    response = client.put("/auth/token", params={"refresh_token": old_refresh_token})
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["access_token"] != old_access_token
    assert response.json()["refresh_token"] != old_refresh_token


def test_register_user(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "username": "test-user-5",
            "password": "_s3cr3tp@5sw0rd_",
            "email": "test-user-3@test.com",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["username"] == "test-user-5"
    assert response.json()["email"] == "test-user-3@test.com"
    assert response.json()["role_id"] == 3  # we assign it to the default "user" role
    assert response.json()["disabled"] == False
    assert response.json()["last_login"]


def test_read_devices_unauthorized(client: TestClient) -> None:
    response = client.get("/devices")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    assert response.json()["detail"]


@pytest.mark.asyncio
async def test_read_devices_authorized(
    client: TestClient, admin_auth_tokens: dict
) -> None:
    # response = client.post(
    #     "/auth/token", data={"username": "test-user-1", "password": "_s3cr3tp@5sw0rd_"}
    # )
    # assert response.status_code == status.HTTP_200_OK, response.text
    # assert response.json()["access_token"]
    # assert response.json()["refresh_token"]

    response = client.get(
        "/devices",
        headers={
            "Authorization": f"Bearer {(await admin_auth_tokens)['access_token']}"
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert (
        len(response.json()["items"]) == 3
    )  # we need to access "items" as we are using pagination


def test_read_devices_expired_token(client: TestClient) -> None:
    # manually created an expired access token for user with id=1 using auth.utils.create_access_token,
    # previously running "export ACCESS_TOKEN_EXPIRE_MINUTES=1"
    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItMSIsImV4cCI6MTcwOTA0MjU0Nn0.1eyTFAnE4qx2ahTl5Z_qgyhCS9QRQAjBuPmhSWXc1Os"

    response = client.get(
        "/devices",
        headers={"Authorization": f"Bearer {expired_access_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text


@pytest.mark.asyncio
async def test_read_tenant_admin(client: TestClient, admin_auth_tokens: dict) -> None:
    tenant_id = 1
    response = client.get(
        f"/tenants/{tenant_id}",
        headers={
            "Authorization": f"Bearer {(await admin_auth_tokens)['access_token']}"
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert data["id"] == tenant_id
    assert data["name"] == "tenant1"
    assert len(data["folders"]) == 4 # 3 manually created +1 (including "/" folder)


@pytest.mark.asyncio
async def test_read_tenant_authorized_owner(
    client: TestClient, owner_2_auth_tokens: dict
) -> None:
    tenant_id = 1
    response = client.get(
        f"/tenants/{tenant_id}",
        headers={
            "Authorization": f"Bearer {(await owner_2_auth_tokens)['access_token']}"
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert data["id"] == tenant_id
    assert data["name"] == "tenant1"
    assert len(data["folders"]) == 4


@pytest.mark.asyncio
async def test_read_tenant_unauthorized_owner(
    client: TestClient, owner_3_auth_tokens: dict
) -> None:
    tenant_id = 1
    response = client.get(
        f"/tenants/{tenant_id}",
        headers={
            "Authorization": f"Bearer {(await owner_3_auth_tokens)['access_token']}"
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text


@pytest.mark.asyncio
async def test_read_tenant_unauthorized_user(
    client: TestClient, user_auth_tokens: dict
) -> None:
    tenant_id = 1
    response = client.get(
        f"/tenants/{tenant_id}",
        headers={"Authorization": f"Bearer {(await user_auth_tokens)['access_token']}"},
    )
    data = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text


@pytest.mark.asyncio
async def test_read_folder_authorized_owner(
    client: TestClient, owner_3_auth_tokens: dict
) -> None:
    folder_id = 6
    response = client.get(
        f"/folders/{folder_id}",
        headers={
            "Authorization": f"Bearer {(await owner_3_auth_tokens)['access_token']}"
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert data["id"] == folder_id
    assert data["name"] == "folder3"
    assert len(data["subfolders"]) == 1


@pytest.mark.asyncio
async def test_read_folder_authorized_admin(
    client: TestClient, admin_auth_tokens: dict
) -> None:
    folder_id = 6
    response = client.get(
        f"/folders/{folder_id}",
        headers={
            "Authorization": f"Bearer {(await admin_auth_tokens)['access_token']}"
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert data["id"] == folder_id
    assert data["name"] == "folder3"
    assert len(data["subfolders"]) == 1


@pytest.mark.asyncio
async def test_read_folder_unauthorized_owner(
    client: TestClient, owner_2_auth_tokens: dict
) -> None:
    folder_id = 6
    response = client.get(
        f"/folders/{folder_id}",
        headers={
            "Authorization": f"Bearer {(await owner_2_auth_tokens)['access_token']}"
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text


@pytest.mark.asyncio
async def test_read_folder_unauthorized_user(
    client: TestClient, user_auth_tokens: dict
) -> None:
    folder_id = 6
    response = client.get(
        f"/folders/{folder_id}",
        headers={"Authorization": f"Bearer {(await user_auth_tokens)['access_token']}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text


@pytest.mark.asyncio
async def test_read_tag_unauthorized_user(
    client: TestClient, user_auth_tokens: dict
) -> None:
    tag_name = ""
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={"Authorization": f"Bearer {(await user_auth_tokens)['access_token']}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text


@pytest.mark.asyncio
async def test_read_tag_authorized_admin(
    client: TestClient, admin_auth_tokens: dict
) -> None:
    tag_name = ""
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={
            "Authorization": f"Bearer {(await admin_auth_tokens)['access_token']}"
        },
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text


@pytest.mark.asyncio
async def test_read_tag_authorized_owner(
    client: TestClient, owner_2_auth_tokens: dict
) -> None:
    tag_name = ""
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={
            "Authorization": f"Bearer {(await owner_2_auth_tokens)['access_token']}"
        },
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
