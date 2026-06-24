import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient


@pytest.mark.order(66)
def test_create_service(
    authenticated_client: TestClient, asset_service, asset_container, service_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])

    response = authenticated_client.post(
        f"/api/v1/asset/{asset_id}/create/service", json={**asset_service}
    )

    assert response.status_code == 201
    service_container.append(response.json())


def test_create_service_with_unauthenticated_client(
    client: TestClient, asset_service, asset_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])
    response = client.post(f"/api/v1/asset/{asset_id}/create/service", json={**asset_service})

    assert response.status_code == 401


@pytest.mark.order(67)
def test_create_service_with_fake_asset_id(
    authenticated_client: TestClient, fake: Faker, asset_service
):
    asset_id = fake.random_int(max=8000000, min=4000)
    response = authenticated_client.post(
        f"/api/v1/asset/{asset_id}/create/service", json={**asset_service}
    )

    assert response.status_code == 404


def test_create_service_with_invalid_expiry_date(
    authenticated_client: TestClient, asset_service, asset_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])

    response = authenticated_client.post(
        f"/api/v1/asset/{asset_id}/create/service",
        json={**asset_service, "expireDate": asset_service["serviceDate"] - 3600 * 24},
    )

    assert response.status_code == 400


@pytest.mark.order(68)
def test_get_service(authenticated_client: TestClient, service_container):
    response = authenticated_client.get("/api/v1/service")
    service_container.append(response.json())
    assert response.status_code == 200


def test_get_service_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/service")

    assert response.status_code == 401


@pytest.mark.order(69)
def test_get_service_with_query_serial_no(authenticated_client: TestClient, asset_container):
    serial_no = random.choice([assets["serialNo"] for assets in asset_container["asset"]["items"]])
    response = authenticated_client.get(f"api/v1/service?q={serial_no}")

    assert response.status_code == 200


@pytest.mark.order(70)
def test_get_service_with_query_asset_type_name(
    authenticated_client: TestClient, asset_type_container
):
    asset_type_name = random.choice(
        [assettype["name"] for assettype in asset_type_container["asset_types"]["items"]]
    )
    response = authenticated_client.get(f"api/v1/service?q={asset_type_name}")

    assert response.status_code == 200


@pytest.mark.order(71)
def test_get_service_with_queries(
    authenticated_client: TestClient, asset_container, asset_type_container
):
    asset_type_name = random.choice(
        [assettype["name"] for assettype in asset_type_container["asset_types"]["items"]]
    )
    serial_no = random.choice([assets["serialNo"] for assets in asset_container["asset"]["items"]])
    response = authenticated_client.get(f"api/v1/service?q={asset_type_name}&q={serial_no}")

    assert response.status_code == 200


@pytest.mark.order(121)
def test_get_service_with_id(authenticated_client: TestClient, service_container):
    service_id = service_container[0]["id"]
    response = authenticated_client.get(f"/api/v1/service/{service_id}")

    assert response.status_code == 200


def test_get_service_with_invalid_id(authenticated_client: TestClient):
    response = authenticated_client.get("/api/v1/service/-1")
    assert response.status_code == 404


def test_get_service_with_unauthenticated(client: TestClient):
    response = client.get("/api/v1/service/-1")
    assert response.status_code == 401


@pytest.mark.order(122)
def test_update_service(authenticated_client: TestClient, service_container, asset_service):
    service_id = service_container[0]["id"]
    response = authenticated_client.put(
        f"/api/v1/asset/{service_id}/update/service",
        json={**asset_service, "expireDate": service_container[0]["serviceDate"] + 3600 * 24},
    )

    assert response.status_code == 200
    assert response.json()["contact"] != service_container[0]["contact"]


def test_update_service_with_unauthenticated(client: TestClient, service_container, asset_service):
    service_id = service_container[0]["id"]
    response = client.put(f"/api/v1/asset/{service_id}/update/service", json={**asset_service})

    assert response.status_code == 401


def test_update_service_with_invalid_id(authenticated_client: TestClient, asset_service):
    response = authenticated_client.put("/api/v1/asset/-1/update/service", json={**asset_service})

    assert response.status_code == 404


@pytest.mark.order(123)
def test_delete_service(authenticated_client: TestClient, service_container):
    service_id = service_container[0]["id"]
    response = authenticated_client.delete(f"/api/v1/service/{service_id}")

    assert response.status_code == 204


def test_delete_service_with_unauthenticated(client: TestClient, service_container):
    service_id = service_container[0]["id"]
    response = client.delete(f"/api/v1/service/{service_id}")

    assert response.status_code == 401


def test_delete_service_with_invalid_id(authenticated_client: TestClient):
    response = authenticated_client.delete("/api/v1/service/-1")

    assert response.status_code == 404
