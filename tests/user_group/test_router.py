import re
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from src import user_group

from src.user_group.constants import ErrorCode
from src.device_group.constants import ErrorCode as ErrorCodeDeviceGroup
from tests.database import app, session

client = TestClient(app)


def test_read_user_groups(session: Session):
    response = client.get("/user_groups/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


def test_read_user_group(session: Session):
    response = client.post("/user_groups/", json={"name": "user-group5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_group_id = data["id"]

    response = client.get(f"/user_groups/{user_group_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_group_id
    assert data["name"] == "user-group5"
    assert data["device_group_id"] is None


def test_read_non_existent_user_group(session: Session):
    user_group_id = 5
    response = client.get(f"/user_groups/{user_group_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_user_group(session: Session):
    response = client.post(
        "/user_groups/", json={"name": "user-group5", "device_group_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "user-group5"
    assert data["device_group_id"] == 1


def test_create_duplicated_user_group(session: Session):
    response = client.post(
        "/user_groups/", json={"name": "user-group1", "device_group_id": 1}
    )  # a user_group with name "user-group1" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_GROUP_NAME_TAKEN


def test_create_user_group_with_device_group_id(session: Session):
    response = client.post(
        "/user_groups/", json={"name": "user-group5", "device_group_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_group_id = data["id"]

    response = client.get(f"/user_groups/{user_group_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "user-group5"
    assert data["device_group_id"] == 1


def test_create_user_group_with_invalid_device_group_id(session: Session):
    response = client.post(
        "/user_groups/", json={"name": "user-group5", "device_group_id": -1}
    )  # a user_group with email "test-user_group@sia.com" was created in session, see: tests/database.py
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCodeDeviceGroup.DEVICE_GROUP_NOT_FOUND


def test_create_user_group_with_invalid_extra_attrs(session: Session):
    response = client.post(
        "/user_groups/",
        json={"name": "user-group5", "tag": "my-custom-tag", "is_admin": True},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_user_group(session: Session):
    # user_group with id=1 already exists in the session. See: tests/database.py
    user_group_id = 1

    response = client.patch(
        f"/user_groups/{user_group_id}", json={"name": "user-group1-updated"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "user-group1-updated"
    assert data["device_group_id"] == 1


def test_update_user_group_with_device_group_id(session: Session):
    response = client.post("/user_groups/", json={"name": "user-group5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_group_id = data["id"]

    response = client.patch(
        f"/user_groups/{user_group_id}",
        json={"name": "user-group5", "device_group_id": 1},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_group_id = data["id"]
    assert data["name"] == "user-group5"
    assert data["device_group_id"] == 1


def test_update_user_group_with_invalid_device_group_id(session: Session):
    response = client.post("/user_groups/", json={"name": "user-group5"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_group_id = data["id"]

    response = client.patch(
        f"/user_groups/{user_group_id}",
        json={"name": "user-group5", "device_group_id": 5},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == ErrorCodeDeviceGroup.DEVICE_GROUP_NOT_FOUND


def test_update_user_group_with_name_taken(session: Session):
    # user_group with id=1 already exists in the session. See: tests/database.py
    user_group_id = 1

    response = client.patch(
        f"/user_groups/{user_group_id}",
        json={"name": "user-group2"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == ErrorCode.USER_GROUP_NAME_TAKEN


def test_update_non_existent_user_group(session: Session):
    user_group_id = 5

    response = client.patch(
        f"/user_groups/{user_group_id}",
        json={"name": "user-group-5-updated"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_non_existent_user_group_attrs(session: Session):
    user_group_id = 1
    response = client.patch(
        f"/user_groups/{user_group_id}",
        json={
            "name": "user-group-1-updated",
            "is_admin": False,  # non existing field
            "tag": "my-cool-user_group-tag",  # non existing field
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_user_group(session: Session):
    response = client.post("/user_groups/", json={"name": "user-group-delete"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    user_group_id = data["id"]

    response = client.delete(f"/user_groups/{user_group_id}")
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/user_groups/{user_group_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_user_group(session: Session):
    user_group_id = 5
    response = client.delete(f"/user_groups/{user_group_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_users(session: Session):
    user_id = 3  # user with id=3 is not in a user group
    response = client.get(f"/users/{user_id}")
    user_data = response.json()
    assert len(user_data["user_groups"]) == 0

    # user_group id=2 has no users
    user_group_id = 2
    response = client.get(f"/user_groups/{user_group_id}/users")
    users_in_user_group_data = response.json()
    assert len(users_in_user_group_data) == 0

    # adding the new user to an existing user group
    response = client.patch(f"/user_groups/{user_group_id}/users", json=[user_data])
    assert response.status_code == status.HTTP_200_OK

    # confirming the new user was added to the user group "users" list
    updated_user_group = response.json()
    user_in_user_groups_ids = (user["id"] for user in updated_user_group["users"])
    assert user_id in user_in_user_groups_ids

    # confirming the user has the user group in its "user_groups" list
    response = client.get(f"/users/{user_id}")
    updated_user_data = response.json()
    user_group_ids_in_user = (ug["id"] for ug in updated_user_data["user_groups"])
    assert user_group_id in user_group_ids_in_user


def test_delete_users(session: Session):
    # user_group id=1 has two users
    user_group_id = 1
    response = client.get(f"/user_groups/{user_group_id}/users")
    users_in_user_group_data = response.json()
    assert len(users_in_user_group_data) == 2

    user_id = 1
    response = client.get(f"/users/{user_id}")
    user = response.json()
    assert len(user["user_groups"]) == 1

    response = client.patch(f"/user_groups/{user_group_id}/users/delete", json=[user])
    updated_user_group = response.json()
    assert len(updated_user_group["users"]) == 1

    response = client.get(f"/users/{user_id}")
    user = response.json()
    assert len(user["user_groups"]) == 0


def test_get_users_from_user_group(session: Session):
    user_group_id = 1
    response = client.get(f"/user_groups/{user_group_id}/users")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
