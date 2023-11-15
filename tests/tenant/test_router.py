from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status

from src.tenant.constants import ErrorCode
from tests.database import app, session

client = TestClient(app)


def test_read_tenants(session: Session):
    response = client.get("/tenants/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_read_tenant(session: Session):
    response = client.post("/tenants/", json={"name": "tenant2"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    tenant_id = data["id"]

    response = client.get(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == tenant_id
    assert data["name"] == "tenant2"
    assert len(data["device_groups"]) == 0


def test_read_non_existent_tenant(session: Session):
    tenant_id = 5
    response = client.get(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_tenant(session: Session):
    response = client.post("/tenants/", json={"name": "tenant2"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "tenant2"
    assert len(data["device_groups"]) == 0


def test_create_tenant_with_device_group(session: Session):
    device_group_id = 2
    response = client.get(f"/device_groups/{device_group_id}")
    device_group_data = response.json()

    response = client.post(
        "/tenants/", json={"name": "tenant2", "device_groups": [device_group_data]}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_duplicated_tenant(session: Session):
    response = client.post(
        "/tenants/", json={"name": "tenant1"}
    )  # "tenant1" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.TENANT_NAME_TAKEN


def test_create_incomplete_tenant(session: Session):
    # attempting to create a new tenant without a "name" value
    response = client.post("/tenants/", json={"groups": []})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_tenant(session: Session):
    # Tenant with id=1 already exists in the session. See: tests/database.py
    tenant_id = 1

    # updating tenant's name
    response = client.patch(
        f"/tenants/{tenant_id}",
        json={"name": "tenant1-updated"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "tenant1-updated"
    assert len(data["device_groups"]) == 1


def test_update_non_existent_tenant(session: Session):
    tenant_id = 5

    response = client.patch(
        f"/tenants/{tenant_id}",
        json={"name": "tenant5-updated"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_non_existent_tenant_attrs(session: Session):
    tenant_id = 1  
    response = client.patch(
        f"/tenants/{tenant_id}",
        json={
            "name": "tenant1-updated",
            "is_admin": False,  # non existing field
            "tag": "my-cool-tenant-tag",  # non existing field
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_delete_tenant(session: Session):
    response = client.post("/tenants/", json={"name": "tenant5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    tenant_id = data["id"]

    response = client.delete(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_tenant(session: Session):
    tenant_id = 5
    response = client.delete(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
