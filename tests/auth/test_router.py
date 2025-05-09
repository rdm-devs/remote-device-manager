import os
import time
import pytest
from typing import Optional
from dotenv import load_dotenv
from jose import jwt
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.constants import ErrorCode
from src.user.schemas import User
from tests.database import (
    app,
    session,
    client_fixture,
    client_authenticated,
    mock_os_data,
    mock_vendor_data,
    admin_auth_tokens,
    owner_2_auth_tokens,
    owner_3_auth_tokens,
    user_auth_tokens,
    get_auth_tokens_with_user_id,
    get_expired_access_token,
    expire_refresh_token,
)

load_dotenv()


def test_login(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        data={"username": "test-user-1@sia.com", "password": "_s3cr3tp@5sw0rd_"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    decoded_token = jwt.decode(
        data["access_token"],
        key=os.getenv("SECRET_KEY"),
        algorithms=[os.getenv("ALGORITHM")],
    )
    user = User.model_validate_json(decoded_token["sub"])
    assert user.role_name is not None


@pytest.mark.asyncio
async def test_device_login(session: Session, client: TestClient) -> None:
    # login in sending a serial number
    device_id = 1
    user_id = 1
    serial_number = "DeviceSerialno0001"
    response = client.post(
        f"/auth/token?serial_number={serial_number}",
        data={
            "username": "test-user-1@sia.com",
            "password": "_s3cr3tp@5sw0rd_",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    refresh_token = data["refresh_token"]

    # login in with the device
    response = client.post(
        f"/auth/device/{device_id}/login",
        json={"refresh_token": expire_refresh_token(session, user_id, refresh_token)},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["device"]


@pytest.mark.asyncio
async def test_logout(client: TestClient, admin_auth_tokens: dict) -> None:
    # then we keep the refresh_token in order to logout
    refresh_token = (await admin_auth_tokens)["refresh_token"]
    response = client.delete("/auth/token", params={"refresh_token": refresh_token})
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["msg"]


@pytest.mark.asyncio
async def test_refresh_token(
    client: TestClient, get_expired_access_token: dict
) -> None:
    # keeping the old access and refresh tokens to compare them with the refresh token endpoint result
    tokens = await get_expired_access_token
    old_access_token = tokens["access_token"]
    old_refresh_token = tokens["refresh_token"]

    response = client.put("/auth/token", params={"refresh_token": old_refresh_token})
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["access_token"] != old_access_token
    assert response.json()["refresh_token"] == old_refresh_token


def test_register_user(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "username": "test-user-5@test.com",
            "password": "_s3cr3tp@5sw0rd_",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["username"] == "test-user-5@test.com"
    assert response.json()["role_id"] == 3  # we assign it to the default "user" role
    assert response.json()["disabled"] == False
    assert response.json()["last_login"]
    assert response.json()["entity_id"]


def test_read_devices_unauthorized(client: TestClient) -> None:
    response = client.get("/devices")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    assert response.json()["detail"]


@pytest.mark.asyncio
async def test_read_devices_authorized(
    client: TestClient, admin_auth_tokens: dict
) -> None:

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
    assert len(data["folders"]) == 4  # 3 manually created +1 (including "/" folder)


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
    assert response.status_code == status.HTTP_200_OK, response.text


@pytest.mark.asyncio
async def test_read_tag_authorized_admin(
    client: TestClient, admin_auth_tokens: dict
) -> None:
    access_tokens = (await admin_auth_tokens)["access_token"]

    tag_name = ""
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 15

    # filtering by name
    tag_name = "tenant1"
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 4

    # filtering by tenant_id
    tenant_id = 1
    response = client.get(
        f"/tags/?tenant_id={tenant_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 3

    # filtering by tenant_id and name
    name = "test"
    tenant_id = 1
    response = client.get(
        f"/tags/?name={name}&tenant_id={tenant_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 0

    # filtering by device_id
    device_id = 1
    response = client.get(
        f"/tags/?device_id={device_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 2

    # filtering by folder_id
    folder_id = 3
    response = client.get(
        f"/tags/?folder_id={folder_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 3


@pytest.mark.asyncio
async def test_read_tag_authorized_owner_2(
    client: TestClient, owner_2_auth_tokens: dict
) -> None:
    access_tokens = (await owner_2_auth_tokens)["access_token"]

    tag_name = ""
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text

    # filtering by name
    tag_name = "tenant1"
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 0

    # filtering by tenant_id
    tenant_id = 1
    response = client.get(
        f"/tags/?tenant_id={tenant_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 3

    # filtering by tenant_id (wrong one) and name. it should reject the request
    name = "tenant"
    tenant_id = 2
    response = client.get(
        f"/tags/?name={name}&tenant_id={tenant_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text

    # filtering by device_id
    device_id = 1
    response = client.get(
        f"/tags/?device_id={device_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 2

    # filtering by folder_id
    folder_id = 3
    response = client.get(
        f"/tags/?folder_id={folder_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["assigned"]) == 3


@pytest.mark.asyncio
async def test_read_tag_authorized_owner_3(
    client: TestClient, owner_3_auth_tokens: dict
) -> None:
    access_tokens = (await owner_3_auth_tokens)["access_token"]

    tag_name = ""
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 7
    assert len(data["assigned"]) == 2

    # filtering by name
    tag_name = "tenant2"
    response = client.get(
        f"/tags/?name={tag_name}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 3
    assert len(data["assigned"]) == 0

    # filtering by tenant_id
    tenant_id = 2
    response = client.get(
        f"/tags/?tenant_id={tenant_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 7
    assert len(data["assigned"]) == 2

    # filtering by tenant_id (wrong one) and name. it should reject the request
    name = "tenant"
    tenant_id = 1
    response = client.get(
        f"/tags/?name={name}&tenant_id={tenant_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text

    response = client.get(
        f"/tags/",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 7
    assert len(data["assigned"]) == 2

    # filtering by device_id
    device_id = 3
    response = client.get(
        f"/tags/?device_id={device_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 5
    assert len(data["assigned"]) == 1

    # filtering by folder_id
    folder_id = 6
    response = client.get(
        f"/tags/?folder_id={folder_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 4
    assert len(data["assigned"]) == 1

    user_id = 1  # attempting to read tags from a user I don't have access to.
    response = client.get(
        f"/tags/?user_id={user_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text

    user_id = 2
    response = client.get(
        f"/tags/?user_id={user_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text

    response = client.get(
        f"/tags",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 7
    assert len(data["assigned"]) == 2

    tenant_id = 2
    folder_id = 7
    response = client.get(
        f"/tags/?tenant_id={tenant_id}&folder_id={folder_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 4
    assert len(data["assigned"]) == 1

    tenant_id = 2
    folder_id = 7
    response = client.get(
        f"/tags/?folder_id={folder_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK, response.text
    assert len(data["available"]) == 4
    assert len(data["assigned"]) == 1


@pytest.mark.parametrize(
    "params, n_items, expected_status_code",
    [
        ("name=", 15, status.HTTP_200_OK),
        ("name=tenant1", 4, status.HTTP_200_OK),
        ("name=tenant2", 3, status.HTTP_200_OK),
        ("tenant_id=2", 0, status.HTTP_403_FORBIDDEN),
        ("name=tenant&tenant_id=1", 2, status.HTTP_200_OK),
        ("device_id=1", 2, status.HTTP_200_OK),
        ("device_id=3", 0, status.HTTP_403_FORBIDDEN),
        ("device_id=10", 0, status.HTTP_404_NOT_FOUND),
    ],
)
@pytest.mark.asyncio
async def test_read_tag_authorized_user(
    client: TestClient,
    user_auth_tokens: dict,
    params: str,
    n_items: int,
    expected_status_code: int,
) -> None:
    access_tokens = (await user_auth_tokens)["access_token"]

    response = client.get(
        f"/tags/?{params}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == expected_status_code
    if "assigned" in data.keys():
        assert len(data["assigned"]) == n_items


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "auth_user_id, user_id, expected_status_code",
    [
        (1, 1, status.HTTP_200_OK),  # admins can update all users
        (1, 2, status.HTTP_200_OK),
        (1, 3, status.HTTP_200_OK),
        (1, 4, status.HTTP_200_OK),
        (2, 4, status.HTTP_200_OK),
        (
            3,
            4,
            status.HTTP_403_FORBIDDEN,
        ),  # owners only can update users only if they share a tenant
        (4, 4, status.HTTP_403_FORBIDDEN),  # regular users cannot update user objects
    ],
)
async def test_update_user(
    client: TestClient,
    session: Session,
    auth_user_id: int,
    user_id: int,
    expected_status_code: int,
) -> None:
    auth_tokens = await get_auth_tokens_with_user_id(session, auth_user_id)
    access_tokens = auth_tokens["access_token"]

    # we are interested in the response status codes
    response = client.patch(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
        json={},
    )

    data = response.json()
    assert response.status_code == expected_status_code, response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "auth_user_id, user_id, expected_status_code",
    [
        (1, 1, status.HTTP_403_FORBIDDEN),  # admin cannot delete itself
        (1, 2, status.HTTP_200_OK),
        (1, 3, status.HTTP_200_OK),
        (1, 4, status.HTTP_200_OK),
        # regular users and owners cannot delete user objects
        (2, 4, status.HTTP_403_FORBIDDEN),
        (3, 4, status.HTTP_403_FORBIDDEN),
        (4, 4, status.HTTP_403_FORBIDDEN),
    ],
)
async def test_delete_user(
    client: TestClient,
    session: Session,
    auth_user_id: int,
    user_id: int,
    expected_status_code: int,
) -> None:
    auth_tokens = await get_auth_tokens_with_user_id(session, auth_user_id)
    access_tokens = auth_tokens["access_token"]

    # we are interested in the response status codes
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    data = response.json()
    assert response.status_code == expected_status_code


@pytest.mark.asyncio
async def test_send_token_to_rustdesk(
    session: Session,
    mock_os_data: dict,
    mock_vendor_data: dict,
    client: TestClient,
):
    TEST_MAC_ADDR = "61:68:0C:1E:93:7F"
    TEST_IP_ADDR = "96.119.132.46"

    user_id = 1
    auth_tokens = await get_auth_tokens_with_user_id(session, user_id)
    access_tokens = auth_tokens["access_token"]

    response = client.post(
        "/devices/",
        json={
            "name": "dev5",
            "folder_id": 1,
            "os_id": 1,
            "vendor_id": 1,
            "mac_address": TEST_MAC_ADDR,
            "ip_address": TEST_IP_ADDR,
            "id_rust": "myRustDeskId",
            "pass_rust": "myRustDeskPass",
            **mock_os_data,
            **mock_vendor_data,
        },
        headers={"Authorization": f"Bearer {access_tokens}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    device_id = data["id"]  # rustdesk credentials were not configured.
    response = client.get(
        f"/devices/{device_id}/connect",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )
    assert response.status_code == status.HTTP_200_OK
    url = response.json()["url"]

    otp = url.split("otp=")[1]
    response = client.get(f"/auth/device/{device_id}/connect/{otp}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["token"]

    fake_otp = "123456"
    response = client.get(f"/auth/device/{device_id}/connect/{fake_otp}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    invalid_device_id = 2  # rustdesk credentials were not configured.
    response = client.get(
        f"/devices/{invalid_device_id}/connect",
        headers={"Authorization": f"Bearer {access_tokens}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # attempting to get token using invalid device id and valid otp
    response = client.get(f"/auth/device/{invalid_device_id}/connect/{otp}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "auth_user_id, device_id, expected_status_code",
    [
        (1, 1, status.HTTP_200_OK),
        (1, "DeviceSerialno0001", status.HTTP_200_OK),
        (1, 2, status.HTTP_400_BAD_REQUEST),  # dev2 doesn't have rust credentials set
        (1, 3, status.HTTP_400_BAD_REQUEST),  # dev3 doesn't have rust credentials set
        (1, 4, status.HTTP_404_NOT_FOUND),
        (2, 1, status.HTTP_200_OK),
        (2, 2, status.HTTP_400_BAD_REQUEST),  # dev2 doesn't have rust credentials set
        (2, 3, status.HTTP_403_FORBIDDEN),
        (3, 1, status.HTTP_403_FORBIDDEN),
        (3, 2, status.HTTP_403_FORBIDDEN),
        (3, 3, status.HTTP_400_BAD_REQUEST),  # dev3 doesn't have rust credentials set
    ],
)
async def test_share_device(
    client: TestClient,
    session: Session,
    auth_user_id: int,
    device_id: int,
    expected_status_code: int,
) -> None:
    auth_tokens = await get_auth_tokens_with_user_id(session, auth_user_id)
    access_tokens = auth_tokens["access_token"]

    response = client.post(
        f"/devices/{device_id}/share",
        headers={"Authorization": f"Bearer {access_tokens}"},
        json={"expiration_minutes": 1},
    )

    data = response.json()
    if "detail" in data:
        print(data["detail"])
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "serial_number, expected_device_id, expected_status_code",
    [
        ("DeviceSerialno0001", 1, status.HTTP_200_OK),
        ("DeviceSerialno0002", 2, status.HTTP_200_OK),
        ("DeviceSerialno0003", 3, status.HTTP_200_OK),
        ("DeviceSerialno0004", 4, status.HTTP_200_OK),
        (None, None, status.HTTP_200_OK),
        (0, None, status.HTTP_200_OK),
    ],
)
def test_login_with_device_serial_number(
    session: Session,
    client: TestClient,
    serial_number: str,
    expected_device_id: int,
    expected_status_code: int,
) -> None:
    response = client.post(
        f"/auth/token/?serial_number={serial_number}",
        data={"username": "test-user-1@sia.com", "password": "_s3cr3tp@5sw0rd_"},
    )
    assert response.status_code == expected_status_code, response.text
    data = response.json()
    device = data["device"]

    if device:
        assert device["id"] == expected_device_id
    else:
        assert device == None


@pytest.mark.asyncio
async def test_login_with_and_without_a_device(
    session: Session,
    client: TestClient,
) -> None:

    def login(serial_number: Optional[str] = None) -> str:
        url = (
            f"/auth/token/?serial_number={serial_number}"
            if serial_number
            else "/auth/token"
        )

        response = client.post(
            url,
            data={"username": "test-user-1@sia.com", "password": "_s3cr3tp@5sw0rd_"},
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        refresh_token = data["refresh_token"]
        return refresh_token

    rt1 = login()
    rt2 = login()
    rt3 = login("DeviceSerialno0001")
    rt4 = login("DeviceSerialno0001")
    rt5 = login("DeviceSerialno0002")
    assert rt1 == rt2
    assert rt2 != rt3
    assert rt3 == rt4
    assert rt4 != rt5


@pytest.mark.asyncio
async def test_reset_password(
    session: Session,
    client: TestClient,
    client_authenticated: TestClient
) -> None:
    user_id = 1
    auth_tokens = get_auth_tokens_with_user_id(session, user_id)
    access_tokens = (await auth_tokens)["access_token"]

    response = client_authenticated.post(
        "/auth/password-reset",
        json={
            "password": "_s3cr3tp@5sw0rd_",
            "new_password": "_s3cr3tp@5sw0rd_",
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    user_id = 3
    response = client.post(
        "/auth/password-reset",
        json={
            "user_id": user_id,
            "new_password": "_s3cr3tp@5sw0rd_",
        },
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json() 


@pytest.mark.asyncio
async def test_reset_password_invalid_permissions(
    session: Session, client: TestClient, user_auth_tokens: dict
) -> None:
    user_id = 4
    access_token = (await user_auth_tokens)["access_token"]

    response = client.post(
        "/auth/password-reset",
        json={
            "password": "_s3cr3tp@5sw0rd_",
            "new_password": "_s3cr3tp@5sw0rd_",
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    user_id = 2
    response = client.post(
        "/auth/password-reset",
        json={
            "user_id": 1,
            "new_password": "_s3cr3tp@5sw0rd_",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()


@pytest.mark.asyncio
async def test_reset_password_invalid_current_password(
    session: Session,
    client: TestClient,
    client_authenticated: TestClient
) -> None:
    user_id = 1
    auth_tokens = get_auth_tokens_with_user_id(session, user_id)
    access_tokens = (await auth_tokens)["access_token"]

    response = client_authenticated.post(
        "/auth/password-reset",
        json={
            "password": "123456789",
            "new_password": "_s3cr3tp@5sw0rd_",
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()

@pytest.mark.asyncio
async def test_reset_password_invalid_new_password(
    session: Session, client: TestClient, client_authenticated: TestClient
) -> None:
    user_id = 1
    auth_tokens = get_auth_tokens_with_user_id(session, user_id)
    access_tokens = (await auth_tokens)["access_token"]

    response = client_authenticated.post(
        "/auth/password-reset",
        json={
            "password": "_s3cr3tp@5sw0rd_",
            "new_password": "1234",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()

    user_id = 1
    response = client.post(
        "/auth/password-reset",
        json={
            "user_id": user_id,
            "new_password": "1234",
        },
        headers={"Authorization": f"Bearer {access_tokens}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
