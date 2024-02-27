import pdb
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.constants import ErrorCode
from tests.database import app, session, client_fixture, mock_os_data, mock_vendor_data

# client = TestClient(app)


def test_login(client: TestClient):
    response = client.post(
        "/auth/token", data={"username": "test-user-1", "password": "_s3cr3tp@5sw0rd_"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


def test_logout(client: TestClient):
    # first we login
    response = client.post(
        "/auth/token", data={"username": "test-user-1", "password": "_s3cr3tp@5sw0rd_"}
    )
    assert response.status_code == 200, response.text
    # then we keep the refresh_token in order to logout
    refresh_token = response.json()["refresh_token"]
    response = client.delete("/auth/token", params={"refresh_token": refresh_token})
    assert response.status_code == 200, response.text
    assert response.json()["msg"]


def test_refresh_token(client: TestClient):
    # first we login
    response = client.post(
        "/auth/token", data={"username": "test-user-1", "password": "_s3cr3tp@5sw0rd_"}
    )
    assert response.status_code == 200, response.text
    # keeping the old access and refresh tokens to compare them with the refresh token endpoint result
    old_access_token = response.json()["access_token"]
    old_refresh_token = response.json()["refresh_token"]

    response = client.put("/auth/token", params={"refresh_token": old_refresh_token})
    assert response.status_code == 200, response.text
    assert response.json()["access_token"] == old_access_token
    assert response.json()["refresh_token"] != old_refresh_token


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "username": "test-user-3",
            "password": "_s3cr3tp@5sw0rd_",
            "email": "test-user-3@test.com",
            "role_id": None,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["username"] == "test-user-3"
    assert response.json()["email"] == "test-user-3@test.com"
    assert response.json()["role_id"] == None
    assert response.json()["disabled"] == False
    assert response.json()["last_login"]
