import pytest
from faker import Faker
from fastapi.testclient import TestClient


@pytest.mark.order(20)
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


@pytest.mark.order(21)
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


@pytest.mark.order(22)
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


@pytest.mark.order(23)
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


@pytest.mark.order(24)
def test_change_user_password(authenticated_client: TestClient, user_data, user_data_factory):
    response = authenticated_client.post(
        "/api/v1/user/password/change/",
        json={
            "oldPassword": user_data["credentials"]["password"],
            "newPassword": user_data_factory()["credentials"]["password"],
        },
    )

    assert response.status_code == 200


@pytest.mark.order(25)
def test_change_user_password_with_unauthenticated_client(client: TestClient, user_data_factory):
    response = client.post(
        "/api/v1/user/password/change/",
        json={
            "oldPassword": user_data_factory()["credentials"]["password"],
            "newPassword": user_data_factory()["credentials"]["password"],
        },
    )

    assert response.status_code == 401


@pytest.mark.order(25)
def test_change_user_password_with_wrong_old_password(
    authenticated_client: TestClient, user_data_factory
):
    response = authenticated_client.post(
        "/api/v1/user/password/change/",
        json={
            "oldPassword": user_data_factory()["credentials"]["password"],
            "newPassword": user_data_factory()["credentials"]["password"],
        },
    )

    assert response.status_code == 401


@pytest.mark.order(26)
def test_get_user_profile(authenticated_client: TestClient):
    response = authenticated_client.get("/api/v1/user/profile")

    assert response.status_code == 200


@pytest.mark.order(27)
def test_get_user_profile_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/user/profile")

    assert response.status_code == 401


@pytest.mark.order(28)
def test_get_org_all_users(authenticated_client: TestClient):
    response = authenticated_client.get("/api/v1/organization/users")

    assert response.status_code == 200
    assert response.json()["total"] != 0


@pytest.mark.order(29)
def test_get_org_all_users_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/organization/users")

    assert response.status_code == 401
