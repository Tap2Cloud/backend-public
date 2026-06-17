import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(2)
def test_authentication(client: TestClient, user_data) -> None:
    response = client.post("/api/v1/login", json=user_data["credentials"])

    assert response.status_code == 200
    assert {"refresh_token", "access_token"} <= response.json().keys()


def test_authentication_without_password(client: TestClient, user_data) -> None:
    response = client.post("/api/v1/login", json={"email": user_data["credentials"]["email"]})

    assert response.status_code == 422
