import json
import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient


@pytest.mark.order(4)
def test_create_organization_with_location(
    authenticated_client: TestClient,
    fake: Faker,
    location,
    organization,
    container,
    taxonomy_container,
):
    response = authenticated_client.post(
        "/api/v1/organization",
        data={
            **organization,
            "taxonomy": json.dumps(random.choice(taxonomy_container["taxonomies"])),
            "location": json.dumps(location),
        },
        files=[("logo", ("file", fake.image(), "application/octet-stream"))],
    )
    container["location"] = response.json()
    container["organization_id"] = response.json()["id"]

    assert response.status_code == 200


@pytest.mark.order(4)
def test_create_organization_with_location_for_second_user(
    authenticated_client: TestClient,
    fake: Faker,
    second_user_data,
    location,
    organization,
    container,
    taxonomy_container,
):
    response = authenticated_client.post("/api/v1/login", json=second_user_data["credentials"])
    response = authenticated_client.post(
        "/api/v1/organization",
        data={
            **organization,
            "taxonomy": json.dumps(random.choice(taxonomy_container["taxonomies"])),
            "location": json.dumps(location),
        },
        files=[("logo", ("file", fake.image(), "application/octet-stream"))],
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )

    container["second_location"] = response.json()
    container["second_organization_id"] = response.json()["id"]

    assert response.status_code == 200


def test_create_organization_without_location(
    authenticated_client: TestClient, organization
) -> None:
    response = authenticated_client.post(
        "/api/v1/organization",
        json={"organization": organization},
    )

    assert response.status_code == 422


def test_create_organization_with_location_only(authenticated_client: TestClient, location) -> None:
    response = authenticated_client.post(
        "/api/v1/organization",
        json={"location": location},
    )

    assert response.status_code == 422


def test_create_organization_without_organization_name_only(
    authenticated_client: TestClient, location, organization
) -> None:
    response = authenticated_client.post(
        "/api/v1/organization",
        json={
            "location": location,
            "organization": {
                "number": organization["number"],
                "email": organization["email"],
            },
        },
    )

    assert response.status_code == 422


def test_create_organization_with_unauthenticated_client(
    client: TestClient, location, organization
) -> None:
    response = client.post(
        "/api/v1/organization",
        json={"organization": organization, "location": location},
    )

    assert response.status_code == 401


def test_get_organization_roles(authenticated_client: TestClient):
    response = authenticated_client.get("/api/v1/organization/roles")

    assert response.status_code == 200


def test_get_organization_roles_with_unauthenticated_client(client: TestClient):
    response = client.get(
        "/api/v1/organization/roles",
    )

    assert response.status_code == 401


@pytest.mark.order(124)
def test_get_organization_with_id(authenticated_client: TestClient, organization_container):
    response = authenticated_client.get(
        "/api/v1/organization",
    )

    assert response.status_code == 200
    organization_container.update(**response.json())


def test_get_organization_with_unauthenticated_client(client: TestClient):
    response = client.get(
        "/api/v1/organization",
    )

    assert response.status_code == 401


@pytest.mark.order(125)
def test_update_organization_with_id(
    authenticated_client: TestClient, organization_container, organization
):
    response = authenticated_client.put(
        "/api/v1/organization",
        data={**organization, "logo": None},
    )

    assert response.status_code == 200
    assert response.json()["name"] != organization_container["name"]


def test_update_organization_with_unauthenticated_client(client: TestClient, organization):
    response = client.put(
        "/api/v1/organization",
        data={**organization, "logo": None},
    )

    assert response.status_code == 401
