from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from src import device, folder
from src.folder.constants import ErrorCode
from tests.database import app, session

client = TestClient(app)


def test_read_folders(session: Session):
    response = client.get("/folders/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_read_folder(session: Session):
    response = client.post("/folders/", json={"name": "folder5", "tenant_id": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    folder_id = data["id"]

    response = client.get(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == folder_id
    assert data["name"] == "folder5"
    assert data["tenant_id"] == 1


def test_read_non_existent_folder(session: Session):
    folder_id = 5
    response = client.get(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_folder(session: Session):
    response = client.post("/folders/", json={"name": "folder5", "tenant_id": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "folder5"
    assert data["tenant_id"] == 1


def test_create_duplicated_folder(session: Session):
    response = client.post(
        "/folders/", json={"name": "folder1", "tenant_id": 1}
    )  # "folder1" was created in session, see: database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.FOLDER_NAME_TAKEN


def test_create_folder_with_invalid_tenant_id(session: Session):
    response = client.post(
        "/folders/", json={"name": "folder5", "tenant_id": 5}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_incomplete_folder(session: Session):
    response = client.post("/folders/", json={"tenant_id": 1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_folder(session: Session):
    folder_id = (
        1  # Folder with id=1 already exists in the session. See: tests/database.py
    )

    response = client.patch(
        f"/folders/{folder_id}",
        json={"name": "folder5-updated"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "folder5-updated"
    assert data["tenant_id"] == 1


def test_update_folder_to_add_a_tenant(session: Session):
    # first we create a tenant
    response = client.post("/tenants/", json={"name": "tenant2"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    tenant_id = data["id"]

    folder_id = 2

    # then we update an existing device group and associate it with our tenant_id
    tenant_id = data["id"]
    response = client.patch(
        f"/folders/{folder_id}",
        json={"name": "folder2-updated", "tenant_id": tenant_id},
    )
    assert response.status_code == status.HTTP_200_OK
    folder_data = response.json()
    assert folder_data["name"] == "folder2-updated"
    assert folder_data["tenant_id"] == tenant_id

    # lastly, we confirm a new device group has been added to our tenant's info.
    response = client.get(f"/tenants/{tenant_id}")
    data = response.json()
    assert folder_data in data["folders"]


def test_update_non_existent_folder(session: Session):
    folder_id = 5

    response = client.patch(
        f"/folders/{folder_id}",
        json={"name": "folder5-updated"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_non_existent_folder_attrs(session: Session):
    folder_id = (
        1  # Folder with id=1 already exists in the session. See: tests/database.py
    )

    response = client.patch(
        f"/folders/{folder_id}",
        json={
            "name": "folder1",
            "tenant_id": None,
            "devices": [],  # non existing field
            "tag": "my-cool-device-group-tag",  # non existing field
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_folder(session: Session):
    response = client.post("/folders/", json={"name": "folder5", "tenant_id": 1})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    folder_id = data["id"]

    response = client.delete(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_device(session: Session):
    folder_id = 5
    response = client.delete(f"/folders/{folder_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
