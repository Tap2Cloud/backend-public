import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(after="test_register.py::test_register_without_firstname_lastname")
def test_authentication(client: TestClient, user_data) -> None:
    response = client.post("/api/v1/login", json=user_data["credentials"])

    assert response.status_code == 200
    assert {"refresh_token", "access_token"} <= response.json().keys()


@pytest.mark.order(after="test_authentication")
def test_authentication_without_password(client: TestClient, user_data) -> None:
    response = client.post("/api/v1/login", json={"email": user_data["credentials"]["email"]})

    assert response.status_code == 422
