import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from utils.enums import InputType


@pytest.mark.order(after="test_user.py::test_get_org_all_users_with_unauthenticated_client")
def test_get_asset_type_category_group(
    authenticated_client: TestClient, asset_type_category_group_container
):
    response = authenticated_client.get("/api/v1/asset-type-category-group")

    asset_type_category_group_container["field_group"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_type_category_group")
def test_create_asset_type_category_string(
    authenticated_client: TestClient,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["string_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_string")
def test_create_asset_type_category_string_for_second_user(
    second_user_client: TestClient,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    response = second_user_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["second_string_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_string_for_second_user")
def test_create_asset_type_category_integer(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.number

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["integer_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_integer")
def test_create_asset_type_category_time(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.time

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["time_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_time")
def test_create_asset_type_category_url(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.url

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["url_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_url")
def test_create_asset_type_category_password(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.password

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["password_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_password")
def test_create_asset_type_category_image(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.image

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["image_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_image")
def test_create_asset_type_category_file(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.file

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["file_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_file")
def test_create_asset_type_category_email(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.email

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["email_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_email")
def test_create_asset_type_category_date(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.date

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["date_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_date")
def test_create_asset_type_category_datetime(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
):
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.datetime

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["datetime_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_datetime")
def test_create_asset_type_category_radio(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    asset_type_category_field_options,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.radio
    asset_type_category_field["options"] = asset_type_category_field_options

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["radio_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_radio")
def test_create_asset_type_category_multiselect(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    asset_type_category_field_options,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.multiselect
    asset_type_category_field["options"] = asset_type_category_field_options

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["multiselect_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_multiselect")
def test_create_asset_type_category_checkbox(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_fields,
    asset_type_category_field_options,
    container,
    asset_type_category_group_container,
):
    asset_type_category_fields[0]["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category_fields[0]["name"] = fake.name()
    asset_type_category_fields[0]["fieldType"] = InputType.checkbox
    asset_type_category_fields[0]["options"] = asset_type_category_field_options

    asset_type_category_fields[-1]["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category_fields[-1]["name"] = fake.name()
    asset_type_category_fields[-1]["fieldType"] = InputType.checkbox
    asset_type_category_fields[-1]["options"] = asset_type_category_field_options

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": asset_type_category_fields,
        },
    )
    container["checkbox_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_checkbox")
def test_create_asset_type_category_select(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    asset_type_category_field_options,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.select
    asset_type_category_field["options"] = asset_type_category_field_options

    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )
    container["select_type_asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_create_asset_type_category_select")
def test_get_asset_type_category(authenticated_client: TestClient):
    response = authenticated_client.get("/api/v1/asset-type-category", headers={"language": "en"})

    assert response.status_code == 200


@pytest.mark.order(after="test_asset_type.py::test_create_asset_type_string_for_second_user")
def test_get_asset_type_category_mapping(
    authenticated_client: TestClient, asset_type_category_mapping_container
):
    response = authenticated_client.get("/api/v1/filter/asset-type-category/mapping")

    asset_type_category_mapping_container["asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_type_category")
def test_get_asset_type_category_by_unauthenticated_client(
    client: TestClient,
):
    response = client.get("/api/v1/asset-type-category", headers={"language": "en"})

    assert response.status_code == 401


@pytest.mark.order(after="test_get_asset_type_category_by_unauthenticated_client")
def test_create_asset_type_category_string_with_unauthenticated_client(
    client: TestClient,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    asset_type_category_field["fieldGroupId"] = random.choice(
        [group["id"] for group in asset_type_category_group_container["field_group"]]
    )
    asset_type_category_field["fieldType"] = InputType.number
    response = client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_create_asset_type_category_string_with_unauthenticated_client")
def test_create_asset_type_category_string_with_fake_group_id(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_category,
    asset_type_category_field,
    container,
):
    asset_type_category["name"] = fake.name()
    asset_type_category_field["fieldType"] = InputType.text
    asset_type_category_field["fieldGroupId"] = fake.random_int(min=100, max=1000)
    response = authenticated_client.post(
        "/api/v1/asset-type-category",
        json={
            "name": asset_type_category["name"],
            "hasTypeplates": asset_type_category["hasTypeplates"],
            "fields": [asset_type_category_field],
        },
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_create_asset_type_category_string_with_fake_group_id")
def test_get_asset_type_category_group_with_unauthenticated_client(
    client: TestClient, asset_type_category_group_container
):
    response = client.get("/api/v1/asset-type-category-group")

    asset_type_category_group_container["field_group"] = response.json()

    assert response.status_code == 401


@pytest.mark.order(after="test_get_asset_type_category_group_with_unauthenticated_client")
def test_get_list_of_asset_type_category_name(
    authenticated_client: TestClient, asset_type_category_detail_container
):
    response = authenticated_client.get("/api/v1/filter/asset-type-category")
    asset_type_category_detail_container["asset_type_category"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_get_list_of_asset_type_category_name")
def test_update_asset_type_category(
    authenticated_client: TestClient,
    container,
    asset_type_category_field,
    asset_type_category,
    asset_type_category_field_options,
):
    updated_asset_type_category = {
        "name": asset_type_category["name"],
        "fields": [
            {
                "id": container["multiselect_asset_type_category"]["fields"][0]["id"],
                **asset_type_category_field,
                "options": [
                    {
                        "id": container["multiselect_asset_type_category"]["fields"][0]["options"][
                            0
                        ]["id"],
                        **asset_type_category_field_options[0],
                    }
                ],
            }
        ],
    }
    response = authenticated_client.patch(
        f"/api/v1/asset-type-category/{container['multiselect_asset_type_category']['id']}",
        json=updated_asset_type_category,
    )

    updated_category = response.json()
    assert response.status_code == 200
    assert updated_category["name"] == updated_asset_type_category["name"]


@pytest.mark.order(after="test_update_asset_type_category")
def test_update_asset_type_category_with_unauthenticated_client(
    client: TestClient,
    container,
    asset_type_category_field,
    asset_type_category,
    asset_type_category_field_options,
):
    updated_asset_type_category = {
        "name": asset_type_category["name"],
        "fields": [
            {
                "id": container["multiselect_asset_type_category"]["fields"][0]["id"],
                **asset_type_category_field,
                "options": [
                    {
                        "id": container["multiselect_asset_type_category"]["fields"][0]["options"][
                            0
                        ]["id"],
                        **asset_type_category_field_options[0],
                    }
                ],
            }
        ],
    }
    response = client.patch(
        f"/api/v1/asset-type-category/{container['multiselect_asset_type_category']['id']}",
        json=updated_asset_type_category,
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_update_asset_type_category_with_unauthenticated_client")
def test_update_asset_type_category_with_invalid_id(
    authenticated_client: TestClient,
    container,
    asset_type_category_field,
    asset_type_category,
    asset_type_category_field_options,
):
    updated_asset_type_category = {
        "name": asset_type_category["name"],
        "fields": [
            {
                "id": container["multiselect_asset_type_category"]["fields"][0]["id"],
                **asset_type_category_field,
                "options": [
                    {
                        "id": container["multiselect_asset_type_category"]["fields"][0]["options"][
                            0
                        ]["id"],
                        **asset_type_category_field_options[0],
                    }
                ],
            }
        ],
    }
    response = authenticated_client.patch(
        "/api/v1/asset-type-category/-1",
        json=updated_asset_type_category,
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_update_asset_type_category_with_invalid_id")
def test_update_asset_type_category_with_invalid_field_id(
    authenticated_client: TestClient,
    container,
    asset_type_category_field,
    asset_type_category,
    asset_type_category_field_options,
):
    updated_asset_type_category = {
        "name": asset_type_category["name"],
        "fields": [
            {
                "id": -1,
                **asset_type_category_field,
                "options": [
                    {
                        "id": container["multiselect_asset_type_category"]["fields"][0]["options"][
                            0
                        ]["id"],
                        **asset_type_category_field_options[0],
                    }
                ],
            }
        ],
    }
    response = authenticated_client.patch(
        f"/api/v1/asset-type-category/{container['multiselect_asset_type_category']['id']}",
        json=updated_asset_type_category,
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_update_asset_type_category_with_invalid_field_id")
def test_asset_type_category_with_invalid_options_id(
    authenticated_client: TestClient,
    container,
    asset_type_category_field,
    asset_type_category,
    asset_type_category_field_options,
):
    updated_asset_type_category = {
        "name": asset_type_category["name"],
        "fields": [
            {
                "id": container["multiselect_asset_type_category"]["fields"][0]["id"],
                **asset_type_category_field,
                "options": [
                    {
                        "id": -1,
                        **asset_type_category_field_options[0],
                    }
                ],
            }
        ],
    }
    response = authenticated_client.patch(
        f"/api/v1/asset-type-category/{container['multiselect_asset_type_category']['id']}",
        json=updated_asset_type_category,
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_asset_type_category_with_invalid_options_id")
def test_asset_type_category_with_duplicate_field_order(
    authenticated_client: TestClient,
    container,
    asset_type_category_field,
    asset_type_category,
    asset_type_category_field_options,
):
    updated_asset_type_category = {
        "name": asset_type_category["name"],
        "fields": [
            {
                "id": container["checkbox_asset_type_category"]["fields"][0]["id"],
                **asset_type_category_field,
                "options": [
                    {
                        "id": container["checkbox_asset_type_category"]["fields"][0]["options"][0][
                            "id"
                        ],
                        **asset_type_category_field_options[0],
                    }
                ],
            },
            {
                "id": container["checkbox_asset_type_category"]["fields"][-1]["id"],
                **asset_type_category_field,
                "options": [
                    {
                        "id": container["checkbox_asset_type_category"]["fields"][-1]["options"][0][
                            "id"
                        ],
                        **asset_type_category_field_options[0],
                    }
                ],
            },
        ],
    }

    response = authenticated_client.patch(
        f"/api/v1/asset-type-category/{container['checkbox_asset_type_category']['id']}",
        json=updated_asset_type_category,
    )

    assert response.status_code == 422


@pytest.mark.order(after="test_asset_type_category_with_duplicate_field_order")
def test_asset_type_category_with_invalid_group_id(
    authenticated_client: TestClient,
    container,
    asset_type_category_field,
    asset_type_category,
    asset_type_category_field_options,
):
    asset_type_category_field["fieldGroupId"] = -1
    updated_asset_type_category = {
        "name": asset_type_category["name"],
        "fields": [
            {
                "id": container["multiselect_asset_type_category"]["fields"][0]["id"],
                **asset_type_category_field,
                "options": [
                    {
                        "id": -1,
                        **asset_type_category_field_options[0],
                    }
                ],
            }
        ],
    }
    response = authenticated_client.patch(
        f"/api/v1/asset-type-category/{container['multiselect_asset_type_category']['id']}",
        json=updated_asset_type_category,
    )

    assert response.status_code == 404
