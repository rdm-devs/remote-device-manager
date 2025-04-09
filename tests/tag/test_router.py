import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from src import device, tag
from src.tag.constants import ErrorCode
from tests.database import (
    app,
    session,
    mock_os_data,
    mock_vendor_data,
    client_authenticated,
    client_fixture,
    admin_auth_tokens,
)


def test_read_tags(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.get("/tags/")
    assert response.status_code == status.HTTP_200_OK
    assert (
        len(response.json()["assigned"]) == 15
    )  # see tags created in tests/database.py + automatic tags (tenants, folders/subfolders)

    response = client_authenticated.get("/tags/?tenant_id=1")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["assigned"]) == 3


def test_read_tag(session: Session, client_authenticated: TestClient) -> None:
    tenant_id = 1
    response = client_authenticated.post(
        "/tags/", json={"name": "tag5", "tenant_id": tenant_id}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    tag_id = data["id"]

    response = client_authenticated.get(f"/tags/{tag_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == tag_id
    assert data["name"] == "tag5"
    assert data["tenant_id"] == tenant_id


def test_read_non_existent_tag(
    session: Session, client_authenticated: TestClient
) -> None:
    tag_id = 20
    response = client_authenticated.get(f"/tags/{tag_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCode.TAG_NOT_FOUND


@pytest.mark.asyncio
async def test_create_tag(
    session: Session, client: TestClient, admin_auth_tokens: dict
) -> None:
    # either auth token should work fine
    token = (await admin_auth_tokens)["access_token"]
    response = client.post(
        "/tags/",
        json={"name": "tag5", "tenant_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "tag5"
    assert data["tenant_id"] == 1


def test_create_duplicated_tag(
    session: Session, client_authenticated: TestClient
) -> None:
    response = client_authenticated.post(
        "/tags/", json={"name": "tag-tenant-1", "tenant_id": 1}
    )  # "tag-tenant-1" was created in session, see: database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.TAG_NAME_TAKEN

    response = client_authenticated.post(
        "/tags/", json={"name": "MENDOZA", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.post(
        "/tags/", json={"name": "Mendoza", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.TAG_NAME_TAKEN

    response = client_authenticated.post(
        "/tags/", json={"name": "mendoza", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.TAG_NAME_TAKEN

    response = client_authenticated.post(
        "/tags/", json={"name": "mendoza-1", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK


def test_create_tag_with_invalid_tenant_id(
    session: Session, client_authenticated: TestClient
) -> None:
    tenant_id = 20
    response = client_authenticated.post(
        "/tags/", json={"name": "tag20", "tenant_id": tenant_id}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_incomplete_tag(
    session: Session, client_authenticated: TestClient
) -> None:
    response = client_authenticated.post("/tags/", json={"tenant_id": 1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_tag(session: Session, client_authenticated: TestClient) -> None:
    tag_id = 1  # See: tests/database.py

    response = client_authenticated.patch(
        f"/tags/{tag_id}",
        json={"name": "tag5-updated"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "tag5-updated"
    assert data["tenant_id"] == 1

    response = client_authenticated.post(
        "/tags/", json={"name": "mendoza1", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.patch(
        f"/tags/{response.json()["id"]}", json={"name": "mendOza1", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.patch(
        f"/tags/{response.json()["id"]}", json={"name": "mendOza1"}
    )
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.post(
        "/tags/", json={"name": "mendoza1-global", "tenant_id": None, "type": "global"}
    )
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.patch(
        f"/tags/{response.json()["id"]}",
        json={"name": "mendOza1-Global", "tenant_id": None},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_tag_to_add_a_tenant(
    session: Session, client_authenticated: TestClient
) -> None:
    # first we create a tenant
    response = client_authenticated.post("/tenants/", json={"name": "tenant3"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    tenant_id = data["id"]

    tag_id = 2

    # then we update an existing tag and associate it with our tenant_id
    response = client_authenticated.patch(
        f"/tags/{tag_id}",
        json={"name": "tag2-updated", "tenant_id": tenant_id},
    )
    assert response.status_code == status.HTTP_200_OK
    tag_data = response.json()
    assert tag_data["name"] == "tag2-updated"
    assert tag_data["tenant_id"] == tenant_id

    # lastly, we confirm a new tag has been added to our tenant's info.
    response = client_authenticated.get(f"/tenants/{tenant_id}/tags")
    data = response.json()["items"]
    assert tag_data in data


def test_update_non_existent_tag(
    session: Session, client_authenticated: TestClient
) -> None:
    tag_id = 20

    response = client_authenticated.patch(
        f"/tags/{tag_id}",
        json={"name": "tag20-updated"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCode.TAG_NOT_FOUND


def test_delete_tag(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/tags/", json={"name": "tag5", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    tag_id = data["id"]

    response = client_authenticated.delete(f"/tags/{tag_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.get(f"/tags/{tag_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_tag(
    session: Session, client_authenticated: TestClient
) -> None:
    tag_id = 20
    response = client_authenticated.delete(f"/tags/{tag_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_tag_multi(session: Session, client_authenticated: TestClient) -> None:

    # creating 2 new tags to delete them after
    response = client_authenticated.post(
        "/tags/", json={"name": "tag-test", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    new_tag = response.json()

    response = client_authenticated.post(
        "/tags/", json={"name": "tag-test-2", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    new_tag_2 = response.json()

    print([new_tag, new_tag_2])
    response = client_authenticated.post(f"/tags/delete", json=[new_tag, new_tag_2])
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
