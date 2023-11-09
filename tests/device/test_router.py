from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from src import device
from src.device.constants import ErrorCode
from src.device_group.constants import ErrorCode as DeviceGroupErrorCode
from tests.database import app, session

client = TestClient(app)


def test_read_devices(session: Session):
    response = client.get("/devices/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_read_device(session: Session):
    response = client.post("/devices/", json={"name": "dev2", "device_group_id": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    device_id = data["id"]

    response = client.get(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == device_id
    assert data["name"] == "dev2"
    assert data["device_group_id"] == 1


def test_create_device(session: Session):
    response = client.post("/devices/", json={"name": "dev2", "device_group_id": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "dev2"
    assert data["device_group_id"] == 1


def test_create_duplicated_device(session: Session):
    response = client.post(
        "/devices/", json={"name": "dev1", "device_group_id": 1}
    )  # "dev1" was created in session, see: database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.DEVICE_NAME_TAKEN


def test_create_incomplete_device(session: Session):
    response = client.post("/devices/", json={"name": "dev2"})
    assert response.status_code == 422, response.text


def test_create_device_with_non_existing_device_group(session: Session):
    response = client.post("/devices/", json={"name": "dev2", "device_group_id": -1})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == DeviceGroupErrorCode.DEVICE_GROUP_NOT_FOUND


def test_update_device(session: Session):
    device_id = 1  # Device with id=1 already exists in the session

    response = client.patch(
        f"/devices/{device_id}", json={"name": "dev2-updated", "device_group_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "dev2-updated"
    assert data["device_group_id"] == 1


def test_update_non_existent_device(session: Session):
    device_id = 5

    response = client.patch(
        f"/devices/{device_id}", json={"name": "dev2-updated", "device_group_id": 1}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCode.DEVICE_NOT_FOUND


def test_update_non_existent_device_attrs(session: Session):
    device_id = 1

    response = client.patch(
        f"/devices/{device_id}", json={"tag": "my-cool-device", "device_group_id": 1}
    )
    assert response.status_code == 422, response.text


def test_update_incomplete_device_attrs(session: Session):
    device_id = 1

    response = client.patch(f"/devices/{device_id}", json={"name": "dev2-updated"})
    assert response.status_code == 422, response.text


def test_delete_device(session: Session):
    device_id = 1  # Device with id=1 already exists in the session

    response = client.delete(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["id"] == device_id


def test_delete_non_existent_device(session: Session):
    device_id = 5

    response = client.delete(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCode.DEVICE_NOT_FOUND
