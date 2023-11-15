from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from src import device, device_group
from src.device_group.constants import ErrorCode
from tests.database import app, session

client = TestClient(app)


def test_read_device_groups(session: Session):
    response = client.get("/device_groups/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_read_device_group(session: Session):
    response = client.post("/device_groups/", json={"name": "dev-group5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    device_group_id = data["id"]

    response = client.get(f"/device_groups/{device_group_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == device_group_id
    assert data["name"] == "dev-group5"
    assert data["tenant_id"] == None


def test_read_non_existent_device_group(session: Session):
    device_group_id = 5
    response = client.get(f"/device_groups/{device_group_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_device_group(session: Session):
    response = client.post("/device_groups/", json={"name": "dev-group5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "dev-group5"
    assert data["tenant_id"] == None


def test_create_duplicated_device_group(session: Session):
    response = client.post(
        "/device_groups/", json={"name": "dev-group1"}
    )  # "dev-group1" was created in session, see: database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.DEVICE_GROUP_NAME_TAKEN


def test_create_device_group_with_invalid_tenant_id(session: Session):
    response = client.post(
        "/device_groups/", json={"name": "dev-group5", "tenant_id": 5}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_incomplete_device_group(session: Session):
    response = client.post("/device_groups/", json={"tenant_id": 1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_device_group(session: Session):
    device_group_id = (
        1  # DeviceGroup with id=1 already exists in the session. See: tests/database.py
    )

    response = client.patch(
        f"/device_groups/{device_group_id}",
        json={"name": "dev-group5-updated", "tenant_id": None},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "dev-group5-updated"
    assert data["tenant_id"] == None


def test_update_device_group_to_add_a_tenant(session: Session):
    # first we create a tenant
    response = client.post("/tenants/", json={"name": "tenant2"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    tenant_id = data["id"]

    device_group_id = 2

    # then we update an existing device group and associate it with our tenant_id
    tenant_id = data["id"]
    response = client.patch(
        f"/device_groups/{device_group_id}",
        json={"name": "dev-group2-updated", "tenant_id": tenant_id},
    )
    assert response.status_code == status.HTTP_200_OK
    device_group_data = response.json()
    assert device_group_data["name"] == "dev-group2-updated"
    assert device_group_data["tenant_id"] == tenant_id

    # lastly, we confirm a new device group has been added to our tenant's info.
    response = client.get(f"/tenants/{tenant_id}")
    data = response.json()
    assert device_group_data in data["device_groups"]


def test_update_non_existent_device_group(session: Session):
    device_group_id = 5

    response = client.patch(
        f"/device_groups/{device_group_id}",
        json={"name": "dev-group5-updated", "tenant_id": None},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_incomplete_device_group(session: Session):
    device_group_id = 1

    response = client.patch(
        f"/device_groups/{device_group_id}",
        json={"tenant_id": 1},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_non_existent_device_group_attrs(session: Session):
    device_group_id = (
        1  # DeviceGroup with id=1 already exists in the session. See: tests/database.py
    )

    response = client.patch(
        f"/device_groups/{device_group_id}",
        json={
            "name": "dev-group1",
            "tenant_id": None,
            "devices": [],  # non existing field
            "tag": "my-cool-device-group-tag",  # non existing field
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_device_group(session: Session):
    response = client.post("/device_groups/", json={"name": "dev-group5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    device_group_id = data["id"]

    response = client.delete(f"/device_groups/{device_group_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/device_groups/{device_group_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_device(session: Session):
    device_group_id = 5
    response = client.delete(f"/device_groups/{device_group_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
