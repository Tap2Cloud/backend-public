import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(5)
def test_update_location(authenticated_client: TestClient, location, container):
    response = authenticated_client.put(
        "/api/v1/location",
        json=location,
    )

    assert response.status_code == 200
    assert response.json()["name"] != container["location"]["name"]


def test_update_location_without_name(authenticated_client: TestClient, location, container):
    response = authenticated_client.put(
        "/api/v1/location",
        json={**location, "name": None},
    )

    assert response.status_code == 422


def test_update_location_with_unauthenticated_client(client: TestClient, location):
    response = client.put(
        "/api/v1/location",
        json=location,
    )

    assert response.status_code == 401


@pytest.mark.order(6)
def test_get_location_list(authenticated_client: TestClient, container):
    response = authenticated_client.get("/api/v1/filter/location")

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_location_list_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/filter/location")

    assert response.status_code == 401
