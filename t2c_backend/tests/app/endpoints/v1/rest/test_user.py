import pytest
from faker import Faker
from fastapi.testclient import TestClient


@pytest.mark.order(76)
def test_update_user_profile(
    authenticated_client: TestClient,
    fake: Faker,
    user_data,
):
    response = authenticated_client.put(
        "/api/v1/user/profile/",
        data={
            "email": user_data["credentials"]["email"],
            "firstName": user_data["basics"]["firstName"],
            "lastName": user_data["basics"]["lastName"],
        },
        files=[("picture", ("file", fake.image(), "application/octet-stream"))],
    )
    user_data["user_id"] = response.json().get("id")
    assert response.status_code == 200


@pytest.mark.order(77)
def test_update_user_profile_with_unauthenticated_client(
    client: TestClient,
    fake: Faker,
    user_data,
):
    response = client.put(
        "/api/v1/user/profile/",
        data={
            "email": user_data["credentials"]["email"],
            "lastName": user_data["basics"]["lastName"],
            "firstName": user_data["basics"]["firstName"],
        },
        files=[("picture", ("file", fake.image(), "application/octet-stream"))],
    )

    assert response.status_code == 401


@pytest.mark.order(78)
def test_update_user_profile_with_updated_data(
    authenticated_client: TestClient,
    fake: Faker,
):
    response = authenticated_client.put(
        "/api/v1/user/profile/",
        data={
            "email": fake.email(),
            "lastName": fake.last_name(),
            "firstName": fake.first_name(),
        },
        files=[("picture", ("file", fake.image(), "application/octet-stream"))],
    )

    assert response.status_code == 200


@pytest.mark.order(79)
def test_update_user_profile_without_image(
    authenticated_client: TestClient,
    fake: Faker,
    user_data,
):
    response = authenticated_client.put(
        "/api/v1/user/profile/",
        data={
            "email": user_data["credentials"]["email"],
            "lastName": user_data["basics"]["lastName"],
            "firstName": user_data["basics"]["firstName"],
        },
    )

    assert response.status_code == 200


@pytest.mark.order(80)
def test_change_user_password(authenticated_client: TestClient, user_data, user_data_factory):
    response = authenticated_client.post(
        "/api/v1/user/password/change/",
        json={
            "oldPassword": user_data["credentials"]["password"],
            "newPassword": user_data_factory()["credentials"]["password"],
        },
    )

    assert response.status_code == 200
