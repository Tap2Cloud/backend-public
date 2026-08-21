import pytest
from fastapi.testclient import TestClient


def test_register(client: TestClient, user_data) -> None:
    response = client.post(
        "/api/v1/register",
        json={**user_data["credentials"], **user_data["basics"]},
    )

    assert response.status_code == 200
    assert {"refresh_token", "access_token"} <= response.json().keys()


@pytest.mark.order(after="test_register")
def test_register_for_second_user(client: TestClient, second_user_data) -> None:
    response = client.post(
        "/api/v1/register",
        json={**second_user_data["credentials"], **second_user_data["basics"]},
    )

    assert response.status_code == 200
    assert {"refresh_token", "access_token"} <= response.json().keys()


@pytest.mark.order(after="test_register_for_second_user")
def test_register_without_password(client: TestClient, user_data) -> None:
    response = client.post(
        "/api/v1/register", json={"email": user_data["credentials"]["email"], **user_data["basics"]}
    )

    assert response.status_code == 422


@pytest.mark.order(after="test_register_without_password")
def test_register_without_email(client: TestClient, user_data) -> None:
    response = client.post(
        "/api/v1/register",
        json={"password": user_data["credentials"]["password"], **user_data["basics"]},
    )

    assert response.status_code == 422


@pytest.mark.order(after="test_register_without_email")
def test_register_without_firstname_lastname(client: TestClient, user_data) -> None:
    response = client.post("/api/v1/register", json={**user_data["credentials"]})

    assert response.status_code == 422
