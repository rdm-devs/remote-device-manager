import os
import pytest
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from src import device
from src.device.constants import ErrorCode
from src.folder.constants import ErrorCode as FolderErrorCode
from tests.database import (
    app,
    session,
    mock_os_data,
    mock_vendor_data,
    client_fixture,
    client_authenticated,
)

TEST_MAC_ADDR = "61:68:0C:1E:93:7F"
TEST_IP_ADDR = "96.119.132.46"


def test_read_devices(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.get("/devices/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 3


def test_read_device(
    session: Session,
    mock_os_data: dict,
    mock_vendor_data: dict,
    client_authenticated: TestClient,
) -> None:
    response = client_authenticated.post(
        "/devices/",
        json={
            "name": "dev5",
            "folder_id": 1,
            "os_id": 1,
            "vendor_id": 1,
            "MAC_addresses": TEST_MAC_ADDR,
            "local_ips": TEST_IP_ADDR,
            "time_zone": "America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    device_id = data["id"]

    response = client_authenticated.get(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == device_id
    assert data["name"] == "dev5"
    assert data["folder_id"] == 1


def test_read_non_existent_device(
    session: Session, client_authenticated: TestClient
) -> None:
    device_id = 5
    response = client_authenticated.get(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_device(
    session: Session,
    mock_os_data: dict,
    mock_vendor_data: dict,
    client_authenticated: TestClient,
) -> None:
    response = client_authenticated.post(
        "/devices/",
        json={
            "name": "dev5",
            "folder_id": 1,
            "os_id": 1,
            "vendor_id": 1,
            "MAC_addresses": TEST_MAC_ADDR,
            "local_ips": TEST_IP_ADDR,
            "time_zone": "America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "dev5"
    assert data["folder_id"] == 1


def test_create_duplicated_device(
    session: Session,
    mock_os_data: dict,
    mock_vendor_data: dict,
    client_authenticated: TestClient,
) -> None:
    response = client_authenticated.post(
        "/devices/",
        json={
            "name": "dev1",
            "folder_id": 1,
            "os_id": 1,
            "vendor_id": 1,
            "MAC_addresses": TEST_MAC_ADDR,
            "local_ips": TEST_IP_ADDR,
            "time_zone": "America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data,
        },
    )  # "dev1" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.DEVICE_NAME_TAKEN

    # a device with that serialno was created in session, see: tests/database.py
    # it will be updated with all the other data.
    serial_number = "DeviceSerialno0001"
    response = client_authenticated.post(
        "/devices/",
        json={
            "name": "dev5",
            "folder_id": 1,
            "os_id": 1,
            "vendor_id": 1,
            "MAC_addresses": TEST_MAC_ADDR,
            "local_ips": TEST_IP_ADDR,
            "time_zone": "America/Argentina/Buenos_Aires",
            "serial_number": serial_number,  # already exists
            **mock_os_data,
            **mock_vendor_data,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "dev5"
    assert response.json()["serial_number"] == serial_number


def test_create_incomplete_device(
    session: Session,
    mock_os_data: dict,
    mock_vendor_data: dict,
    client_authenticated: TestClient,
) -> None:
    response = client_authenticated.post(
        "/devices/",
        json={
            # "name": "dev5",
            "os_id": 1,
            "vendor_id": 1,
            "MAC_addresses": TEST_MAC_ADDR,
            "local_ips": TEST_IP_ADDR,
            **mock_os_data,
            **mock_vendor_data,
        },
    )
    assert response.status_code == 422, response.text


def test_create_device_with_non_existing_folder(
    session: Session,
    mock_os_data: dict,
    mock_vendor_data: dict,
    client_authenticated: TestClient,
) -> None:
    response = client_authenticated.post(
        "/devices/",
        json={
            "name": "dev5",
            "folder_id": -1,
            "os_id": 1,
            "vendor_id": 1,
            "MAC_addresses": TEST_MAC_ADDR,
            "local_ips": TEST_IP_ADDR,
            "time_zone": "America/Argentina/Buenos_Aires",
            **mock_os_data,
            **mock_vendor_data,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == FolderErrorCode.FOLDER_NOT_FOUND


def test_update_device(session: Session, client_authenticated: TestClient) -> None:
    # Device with id=1 already exists in the session. See: tests/database.py
    device_id = 1

    # attempting to assign tags from a tenant with who the device is not related.
    tenant_id = 2
    response = client_authenticated.get(f"/tags/?tenant_id={tenant_id}")
    tags_tenant_2 = response.json()["assigned"]

    response = client_authenticated.get(f"/tags/?device_id={device_id}")
    tags_device_1 = response.json()["assigned"]

    new_tags = [*tags_device_1, *tags_tenant_2]
    response = client_authenticated.patch(
        f"/devices/{device_id}",
        json={
            "name": "dev5-updated",
            "folder_id": 1,
            "tags": new_tags,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "dev5-updated"
    assert data["folder_id"] == 1
    assert all(t not in data["tags"] for t in tags_tenant_2)
    assert all(t in data["tags"] for t in tags_device_1)

    # attempting to assign tags from a tenant with who the device is related.
    tenant_id = 1
    response = client_authenticated.get(f"/tags/?tenant_id={tenant_id}")
    tags_tenant_1 = response.json()["assigned"]

    # in this case the existing tags are included in the list that comes from the tenant
    # that is related to the device being updated.
    new_tags = tags_device_1
    for t in tags_tenant_1:
        if t not in new_tags:  # filtering repeated items (backend ignores them anyway)
            new_tags.append(t)

    response = client_authenticated.patch(
        f"/devices/{device_id}",
        json={"tags": new_tags},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # the operation should succeed and the device should have new tags assigned.
    assert all(t in data["tags"] for t in tags_tenant_1)
    assert all(t in data["tags"] for t in tags_device_1)


def test_update_non_existent_device(
    session: Session, client_authenticated: TestClient
) -> None:
    device_id = 5

    response = client_authenticated.patch(
        f"/devices/{device_id}", json={"name": "dev5-updated", "folder_id": 1}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCode.DEVICE_NOT_FOUND


def test_delete_device(session: Session, client_authenticated: TestClient) -> None:
    root_folder_id = 1 # see tests/database.py 
    device_id = 1  # Device with id=1 already exists in the session
    response = client_authenticated.get(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    original_tags = data["tags"]
    folder_id = data["folder_id"]

    response = client_authenticated.delete(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["id"] == device_id

    response = client_authenticated.get(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["folder_id"] == root_folder_id


def test_delete_non_existent_device(
    session: Session, client_authenticated: TestClient
) -> None:
    device_id = 5

    response = client_authenticated.delete(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCode.DEVICE_NOT_FOUND


def test_connect_to_device(
    session: Session,
    client_authenticated: TestClient,
):
    device_id = 1
    response = client_authenticated.get(f"/devices/{device_id}/connect")
    url = response.json()["url"]
    assert response.status_code == status.HTTP_200_OK
    assert url is not None
    assert "id=" in url
    assert "otp=" in url


@pytest.mark.parametrize(
    "device_id, body, expected_status_code",
    [
        (1, {}, status.HTTP_200_OK),
        (1, {"id_rust": "asd", "pass_rust": "1234"}, status.HTTP_200_OK),
        (1, {"color": "red"}, status.HTTP_200_OK),
    ],
)
def test_update_device_heartbeat(
    device_id: int,
    body: dict,
    expected_status_code: int,
    session: Session,
    client_authenticated: TestClient,
):
    response = client_authenticated.post(f"/devices/{device_id}/heartbeat", json=body)
    device_status = response.json()
    assert response.status_code == expected_status_code
    assert device_status["device_id"] == device_id
    assert device_status["timestamp"] is not None
    if "id_rust" in body or "pass_rust" in body:
        response = client_authenticated.get(f"/devices/{device_id}")
        result = response.json()
        assert result["id_rust"] == body["id_rust"]
        assert result["pass_rust"] == body["pass_rust"]


@pytest.mark.parametrize(
    "device_id, body, expected_status_code",
    [
        (1, {"expiration_minutes": 1}, status.HTTP_200_OK),
        (1, {"expiration_minutes": 0}, status.HTTP_200_OK),
        (1, {"expiration_minutes": -1}, status.HTTP_400_BAD_REQUEST),
        (1, {}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
def test_share_device(
    device_id: int,
    body: dict,
    expected_status_code: int,
    session: Session,
    client_authenticated: TestClient,
):
    response = client_authenticated.post(f"/devices/{device_id}/share", json=body)
    share_data = response.json()
    assert response.status_code == expected_status_code
    if response.status_code == status.HTTP_200_OK:
        assert "url" in share_data


def test_device_is_online(session: Session, client_authenticated: TestClient, client: TestClient):
    device_id = 1  # is offline initially
    response = client_authenticated.get(f"/devices/{device_id}")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "is_online" in data
    assert data["is_online"] == False

    fake_heartbeat = {
        "CPU_load": 0,
        "MEM_load_mb": 0,
        "free_space_mb": 0,
    }

    # sending a heartbeat will recalculate the online status in new readings
    response = client.post(
        f"/devices/{device_id}/heartbeat", json=fake_heartbeat
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK

    # as the heartbeat is recent, the device will show up online
    response = client_authenticated.get(f"/devices/{device_id}")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["is_online"] == True


def test_device_list_with_online_status(session: Session, client_authenticated: TestClient, client: TestClient):
    response = client_authenticated.get(f"/devices")
    devices = response.json()["items"]
    assert response.status_code == status.HTTP_200_OK
    for device in devices:
        assert "is_online" in device.keys()
        assert type(device["is_online"]) == bool

    device_id = 1
    fake_heartbeat = {
        "CPU_load": 0,
        "MEM_load_mb": 0,
        "free_space_mb": 0,
    }

    # sending a heartbeat will recalculate the online status in new readings
    response = client.post(
        f"/devices/{device_id}/heartbeat", json=fake_heartbeat
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK

    # as the heartbeat is recent, the device will show up online
    response = client_authenticated.get(f"/devices")
    devices = response.json()["items"]
    assert response.status_code == status.HTTP_200_OK
    for device in devices:
        assert "id" in device.keys()
        if device_id == device["id"]:
            assert device["is_online"] == True
