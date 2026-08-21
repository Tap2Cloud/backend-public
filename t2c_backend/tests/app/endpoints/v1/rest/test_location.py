import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(
    after="test_organization.py::test_create_organization_role_with_unauthenticated_client",
)
def test_update_location(authenticated_client: TestClient, location, container):
    response = authenticated_client.put(
        "/api/v1/location",
        json=location,
    )

    assert response.status_code == 200
    assert response.json()["city"] != container["location"]["city"]


@pytest.mark.order(after="test_update_location")
def test_update_location_without_city(authenticated_client: TestClient, location, container):
    response = authenticated_client.put(
        "/api/v1/location",
        json={**location, "city": None},
    )

    assert response.status_code == 422


@pytest.mark.order(after="test_update_location_without_city")
def test_update_location_with_unauthenticated_client(client: TestClient, location):
    response = client.put(
        "/api/v1/location",
        json=location,
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_update_location_with_unauthenticated_client")
def test_get_location_list(authenticated_client: TestClient, container):
    response = authenticated_client.get("/api/v1/filter/location")

    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.order(after="test_get_location_list")
def test_get_location_list_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/filter/location")

    assert response.status_code == 401
