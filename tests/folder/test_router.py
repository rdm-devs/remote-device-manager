import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from src import device, folder
from src.folder.constants import ErrorCode
from tests.database import (
    app,
    session,
    mock_os_data,
    mock_vendor_data,
    client_authenticated,
)


def test_read_folders(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.get("/folders/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5


def test_read_folder(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/folders/", json={"name": "folder5", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    folder_id = data["id"]

    response = client_authenticated.get(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == folder_id
    assert data["name"] == "folder5"


def test_read_non_existent_folder(
    session: Session, client_authenticated: TestClient
) -> None:
    folder_id = 16
    response = client_authenticated.get(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_folder(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/folders/", json={"name": "folder5", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "folder5"
    assert data["tenant_id"] == 1


def test_create_duplicated_folder(
    session: Session, client_authenticated: TestClient
) -> None:
    response = client_authenticated.post(
        "/folders/", json={"name": "folder1", "tenant_id": 1}
    )  # "folder1" was created in session, see: database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.FOLDER_NAME_TAKEN


def test_create_folder_with_invalid_tenant_id(
    session: Session, client_authenticated: TestClient
):
    response = client_authenticated.post(
        "/folders/", json={"name": "folder5", "tenant_id": 5}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_incomplete_folder(
    session: Session, client_authenticated: TestClient
) -> None:
    response = client_authenticated.post("/folders/", json={"tenant_id": 1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_folder(session: Session, client_authenticated: TestClient) -> None:
    folder_id = 1  # Folder id=1 already exists in the session. See: tests/database.py

    # attempting to assign tags from a tenant with who the device is not related.
    tenant_id = 2
    response = client_authenticated.get(f"/tags/?tenant_id={tenant_id}")
    tags_tenant_2 = response.json()["assigned"]

    response = client_authenticated.get(f"/tags/?folder_id={folder_id}")
    tags_folder_1 = response.json()["assigned"]

    new_tags = [*tags_folder_1, *tags_tenant_2]
    response = client_authenticated.patch(
        f"/folders/{folder_id}",
        json={"name": "folder5-updated", "tags": new_tags},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "folder5-updated"
    assert data["tenant_id"] == 1
    assert all(t not in data["tags"] for t in tags_tenant_2)
    assert all(t in data["tags"] for t in tags_folder_1)

    # attempting to assign tags from a tenant with who the device is related.
    tenant_id = 1
    response = client_authenticated.get(f"/tags/?tenant_id={tenant_id}")
    tags_tenant_1 = response.json()["assigned"]

    # in this case the existing tags are included in the list that comes from the tenant
    # that is related to the device being updated.
    new_tags = tags_folder_1
    for t in tags_tenant_1:
        if t not in new_tags:  # filtering repeated items (backend ignores them anyway)
            new_tags.append(t)

    response = client_authenticated.patch(
        f"/folders/{folder_id}",
        json={"tags": new_tags},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # the operation should succeed and the device should have new tags assigned.
    assert all(t in data["tags"] for t in tags_tenant_1)
    assert all(t in data["tags"] for t in tags_folder_1)


@pytest.mark.parametrize(
    "folder_id, body, expected_status_code",
    [
        (2, {}, status.HTTP_200_OK),
        (2, {"tags": []}, status.HTTP_200_OK),
        (2, {"devices": []}, status.HTTP_200_OK),
        (2, {"subfolders": []}, status.HTTP_200_OK),
        (2, {"tags": [], "devices": [], "subfolders": []}, status.HTTP_200_OK),
    ],
)
def test_update_folder_with_empty_lists(
    session: Session,
    client_authenticated: TestClient,
    folder_id: int,
    body: dict,
    expected_status_code: int,
) -> None:
    response = client_authenticated.get(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.patch(
        f"/folders/{folder_id}",
        json=body,
    )
    assert response.status_code == expected_status_code


def test_update_folder_tags_doesnt_lose_subfolders_and_devices(
    session: Session, client_authenticated: TestClient
) -> None:
    folder_id = 3
    response = client_authenticated.get(f"/folders/{folder_id}")
    folder = response.json()

    subfolders = folder["subfolders"]
    devices = folder["devices"]
    assert len(subfolders) == 1
    assert len(devices) == 1

    # removing a tag but keeping everything else the same
    folder["tags"].pop()

    response = client_authenticated.patch(
        f"/folders/{folder_id}",
        json={
            "tags": folder["tags"],
            "subfolders": folder["subfolders"],
            "devices": folder["devices"],
        },
    )
    updated_folder = response.json()
    updated_subfolders = updated_folder["subfolders"]
    assert all(f in updated_subfolders for f in subfolders)

    # working with id because heartbeat_timestamp changes when updating a device and prevents a "simpler" any() assert below.
    updated_devices = updated_folder["devices"]
    updated_devices_ids = [d["id"] for d in updated_devices]
    assert all(d["id"] in updated_devices_ids for d in devices)


def test_update_folder_to_add_a_tenant(
    session: Session, client_authenticated: TestClient
) -> None:
    # first we create a tenant
    response = client_authenticated.post("/tenants/", json={"name": "tenant5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    tenant_id = data["id"]

    folder_id = 2

    # then we update an existing folder and associate it with our tenant_id
    response = client_authenticated.patch(
        f"/folders/{folder_id}",
        json={"name": "folder2-updated", "tenant_id": tenant_id},
    )
    assert response.status_code == status.HTTP_200_OK
    folder_data = response.json()
    assert folder_data["name"] == "folder2-updated"
    assert folder_data["tenant_id"] == tenant_id

    # lastly, we confirm a new folder has been added to our tenant's info.
    response = client_authenticated.get(f"/tenants/{tenant_id}")
    data = response.json()
    assert any(
        folder_data["id"] == f["id"] and folder_data["name"] == f["name"]
        for f in data["folders"]
    )


def test_update_non_existent_folder(
    session: Session, client_authenticated: TestClient
) -> None:
    folder_id = 16

    response = client_authenticated.patch(
        f"/folders/{folder_id}",
        json={"name": "folder6-updated"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_folder(session: Session, client_authenticated: TestClient) -> None:
    response = client_authenticated.post(
        "/folders/", json={"name": "folder5", "tenant_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    folder_id = data["id"]

    response = client_authenticated.delete(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client_authenticated.get(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_folder(
    session: Session, client_authenticated: TestClient
) -> None:
    folder_id = 16
    response = client_authenticated.delete(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
