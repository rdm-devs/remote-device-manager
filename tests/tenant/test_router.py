import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status

from src.tenant.constants import ErrorCode
from tests.database import (
    app,
    session,
    mock_os_data,
    mock_vendor_data,
    client_authenticated,
)


def test_read_tenants(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.get("/tenants/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 2


def test_read_tenant(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post("/tenants/", json={"name": "tenant3"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    tenant_id = data["id"]

    response = client_authenticated.get(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == tenant_id
    assert data["name"] == "tenant3"
    assert len(data["folders"]) == 1


def test_read_non_existent_tenant(
    session: Session, client_authenticated: TestClient
) -> None:
    tenant_id = 5
    response = client_authenticated.get(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_tenant(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post("/tenants/", json={"name": "tenant3"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "tenant3"
    assert len(data["folders"]) == 1


def test_create_duplicated_tenant(
    session: Session, client_authenticated: TestClient
) -> None:
    response = client_authenticated.post(
        "/tenants/", json={"name": "tenant1"}
    )  # "tenant1" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.TENANT_NAME_TAKEN


def test_create_incomplete_tenant(
    session: Session, client_authenticated: TestClient
) -> None:
    # attempting to create a new tenant without a "name" value
    response = client_authenticated.post("/tenants/", json={"groups": []})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_tenant(session: Session, client_authenticated: TestClient) -> None:
    # Tenant with id=1 already exists in the session. See: tests/database.py
    tenant_id = 1
    response = client_authenticated.get(f"/tags/?tenant_id={tenant_id}")
    tags_tenant_1 = response.json()["assigned"]

    # attempting to assign tags from another tenant.
    tenant_2_id = 2
    response = client_authenticated.get(f"/tags/?tenant_id={tenant_2_id}")
    tags_tenant_2 = response.json()["assigned"]

    # creating a new tag
    response = client_authenticated.post(
        f"/tags", json={"name": "custom-tag", "tenant_id": tenant_id}
    )
    assert response.status_code == status.HTTP_200_OK
    tag = response.json()

    new_tags = [
        *tags_tenant_1,
        *tags_tenant_2,
        tag,
    ]  # mixing valid and invalid tags (tags from a different tenant)
    response = client_authenticated.patch(
        f"/tenants/{tenant_id}",
        json={"name": "tenant1", "tags": new_tags},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "tenant1"
    assert len(data["folders"]) == 4
    # invalid tags are not in the tenant's tags list
    assert all(t not in data["tags"] for t in tags_tenant_2)
    # valid tags are in the tenant's tags list
    assert all(t in data["tags"] for t in tags_tenant_1)
    assert tag in data["tags"]


def test_update_non_existent_tenant(
    session: Session, client_authenticated: TestClient
) -> None:
    tenant_id = 5

    response = client_authenticated.patch(
        f"/tenants/{tenant_id}",
        json={"name": "tenant5-updated"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_tenant(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post("/tenants/", json={"name": "tenant5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    tenant_id = data["id"]

    response = client_authenticated.delete(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_non_existent_tenant(
    session: Session, client_authenticated: TestClient
) -> None:
    tenant_id = 5
    response = client_authenticated.delete(f"/tenants/{tenant_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "tenant_id, expected_status_code",
    [
        (1, status.HTTP_200_OK),
        (99, status.HTTP_404_NOT_FOUND),
    ],
)
def test_read_tenant_settings(
    session: Session,
    client_authenticated: TestClient,
    tenant_id: int,
    expected_status_code: int,
) -> None:
    response = client_authenticated.get(f"/tenants/{tenant_id}/settings")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "tenant_id, body, expected_status_code",
    [
        (1, {}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (1, {"heartbeat_s": 20}, status.HTTP_200_OK),
        (1, {"heartbeat_s": 20, "color": "red"}, status.HTTP_200_OK),
        (99, {}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (99, {"heartbeat_s": 20}, status.HTTP_404_NOT_FOUND),
    ],
)
def test_update_tenant_settings(
    session: Session,
    client_authenticated: TestClient,
    tenant_id: int,
    body: dict,
    expected_status_code: int,
) -> None:
    response = client_authenticated.patch(f"/tenants/{tenant_id}/settings", json=body)
    assert response.status_code == expected_status_code
