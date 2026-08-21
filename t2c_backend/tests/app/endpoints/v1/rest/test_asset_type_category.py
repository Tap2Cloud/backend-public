import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from t2c_backend.utils.enums import InputType


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
    authenticated_client: TestClient,
    second_user_data,
    asset_type_category,
    asset_type_category_field,
    container,
    asset_type_category_group_container,
):
    response = authenticated_client.post("/api/v1/login", json=second_user_data["credentials"])

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
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
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
    response = client.get("/api/v1/filter/asset-type-category/mapping")
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


@pytest.mark.order(49)
def test_get_list_of_asset_type_category_by_unauthenticated_client(
    client: TestClient,
):
    response = client.get("/api/v1/filter/asset-type-category")

    assert response.status_code == 401


@pytest.mark.order(151)
def test_update_asset_type_category_add_integer_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("integer_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_integer_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.time.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_integer_field],
        },
    )
    container["integer_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(152)
def test_update_asset_type_category_add_time_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("time_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_time_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.time.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_time_field],
        },
    )
    container["time_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(153)
def test_update_asset_type_category_add_url_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("url_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_url_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.url.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_url_field],
        },
    )
    container["url_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(154)
def test_update_asset_type_category_add_text_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("string_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_text_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.text.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_text_field],
        },
    )
    container["string_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(155)
def test_update_asset_type_category_add_password_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("password_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_password_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.password.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_password_field],
        },
    )
    container["password_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(156)
def test_update_asset_type_category_add_image_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("image_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_image_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.image.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_image_field],
        },
    )
    container["image_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(157)
def test_update_asset_type_category_add_file_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("file_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_file_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.file.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_file_field],
        },
    )
    container["file_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(158)
def test_update_asset_type_category_add_email_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("email_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_email_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.email.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_email_field],
        },
    )
    container["email_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(159)
def test_update_asset_type_category_add_date_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("date_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_date_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.date.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_date_field],
        },
    )
    container["date_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(160)
def test_update_asset_type_category_add_datetime_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
):
    existing_category = container.get("datetime_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    new_datetime_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.datetime.value,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_datetime_field],
        },
    )
    container["datetime_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(161)
def test_update_asset_type_category_add_radio_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
    asset_type_category_field_options,
):
    existing_category = container.get("radio_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)
    clean_options = [{**opt, "id": None} for opt in asset_type_category_field_options]
    new_radio_field = {
        **asset_type_category_field,
        "fieldType": InputType.radio.value,
        "id": None,
        "options": clean_options,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_radio_field],
        },
    )
    container["radio_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(162)
def test_update_asset_type_category_add_checkbox_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
    asset_type_category_field_options,
):
    existing_category = container.get("checkbox_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    clean_options = [{**opt, "id": None} for opt in asset_type_category_field_options]

    new_checkbox_field = {
        **asset_type_category_field,
        "fieldType": InputType.checkbox.value,
        "id": None,
        "options": clean_options,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_checkbox_field],
        },
    )
    container["checkbox_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(163)
def test_update_asset_type_category_add_multiselect_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
    asset_type_category_field_options,
):
    existing_category = container.get("multiselect_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)
    clean_options = [{**opt, "id": None} for opt in asset_type_category_field_options]

    new_multiselect_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.multiselect.value,
        "options": clean_options,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_multiselect_field],
        },
    )
    container["multiselect_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(164)
def test_update_asset_type_category_add_select_field(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
    asset_type_category_field_options,
):
    existing_category = container.get("select_type_asset_type_category")
    raw_first_field = existing_category["fields"][0]
    saved_first_field = {**raw_first_field}
    saved_first_field["fieldGroupId"] = saved_first_field["fieldGroup"].get("id")
    saved_first_field.pop("fieldGroup", None)

    clean_options = [{**opt, "id": None} for opt in asset_type_category_field_options]

    new_select_field = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.select.value,
        "options": clean_options,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [saved_first_field, new_select_field],
        },
    )
    container["select_asset_type_category"] = response.json()
    assert response.status_code == 200


@pytest.mark.order(165)
def test_update_asset_type_category_delete_integer_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("integer_asset_type_category")

    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(166)
def test_update_asset_type_category_delete_time_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("time_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(167)
def test_update_asset_type_category_delete_url_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("url_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(168)
def test_update_asset_type_category_delete_text_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("string_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(169)
def test_update_asset_type_category_delete_password_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("password_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(170)
def test_update_asset_type_category_delete_image_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("image_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(171)
def test_update_asset_type_category_delete_file_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("file_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(172)
def test_update_asset_type_category_delete_email_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("email_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(173)
def test_update_asset_type_category_delete_date_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("date_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(174)
def test_update_asset_type_category_delete_datetime_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("datetime_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(175)
def test_update_asset_type_category_delete_checkbox_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("checkbox_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(176)
def test_update_asset_type_category_delete_multiselect_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("multiselect_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(177)
def test_update_asset_type_category_delete_radio_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("radio_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(178)
def test_update_asset_type_category_delete_select_field(
    authenticated_client: TestClient,
    container,
):
    existing_category = container.get("select_type_asset_type_category")
    raw_remaining_field = existing_category["fields"][0]
    remaining_field = {**raw_remaining_field}
    remaining_field["fieldGroupId"] = remaining_field["fieldGroup"].get("id")
    remaining_field.pop("fieldGroup", None)

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [remaining_field],
        },
    )

    assert response.status_code == 200


@pytest.mark.order(179)
def test_update_category_fields_with_simultaneous_add_edit_delete_and_reorder(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_field,
    asset_type_category_field_options,
):
    existing_category = container.get("radio_asset_type_category")
    raw_field_1 = existing_category["fields"][0]
    raw_field_2 = existing_category["fields"][1]

    field_1_original_order = raw_field_1["fieldOrder"]
    field_2_deleted_order = raw_field_2["fieldOrder"]
    group_id = raw_field_1["fieldGroup"]["id"]
    option_a = raw_field_1["options"][0]
    option_b = raw_field_1["options"][1]

    updated_field_1 = {
        "id": raw_field_1["id"],
        "fieldName": fake.word(),
        "fieldPlaceHolder": raw_field_1["fieldPlaceHolder"],
        "fieldDisplayName": raw_field_1["fieldDisplayName"],
        "fieldIsRequired": raw_field_1["fieldIsRequired"],
        "fieldType": raw_field_1["fieldType"],
        "fieldGroupId": group_id,
        "fieldOrder": field_2_deleted_order,
        "options": [
            {"id": None, "optionId": option_a["optionId"], "optionLabel": fake.word()},
            {
                "id": option_b["id"],
                "optionId": option_b["optionId"],
                "optionLabel": option_b["optionLabel"],
            },
        ],
    }

    options = [{**opt, "id": None} for opt in asset_type_category_field_options]
    new_field_3 = {
        **asset_type_category_field,
        "id": None,
        "fieldType": InputType.radio.value,
        "fieldGroupId": group_id,
        "fieldOrder": field_1_original_order,
        "options": options,
    }

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [updated_field_1, new_field_3],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(180)
def test_update_asset_type_category_replace_all_options(
    authenticated_client: TestClient, fake: Faker, container, asset_type_category_field_options
):
    existing_category = container.get("radio_asset_type_category")
    field_to_modify = existing_category["fields"][0]
    options = [{**opt, "id": None} for opt in asset_type_category_field_options]

    updated_field = {
        **field_to_modify,
        "fieldGroupId": field_to_modify["fieldGroup"]["id"],
        "options": options,
    }

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": [updated_field],
        },
    )
    assert response.status_code == 200


@pytest.mark.order(181)
def test_update_asset_type_category_replace_all_fields(
    authenticated_client: TestClient,
    fake: Faker,
    container,
    asset_type_category_fields,
    asset_type_category_group_container,
):
    existing_category = container.get("radio_asset_type_category")

    fields_payload = [
        {
            **field,
            "id": None,
        }
        for field in asset_type_category_fields
    ]

    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{existing_category['id']}",
        json={
            "name": existing_category["name"],
            "hasTypeplates": existing_category["hasTypeplates"],
            "fields": fields_payload,
        },
    )

    assert response.status_code == 200


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
    response = client.put(
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
                "options": [],
            }
        ],
    }
    response = authenticated_client.put(
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
                "options": [],
            }
        ],
    }
    response = authenticated_client.put(
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
                "fieldType": container["multiselect_asset_type_category"]["fields"][0]["fieldType"],
                "options": [
                    {
                        "id": -1,
                        **asset_type_category_field_options[0],
                    }
                ],
            }
        ],
    }
    response = authenticated_client.put(
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

    response = authenticated_client.put(
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
                "options": [],
            }
        ],
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type-category/{container['multiselect_asset_type_category']['id']}",
        json=updated_asset_type_category,
    )

    assert response.status_code == 404
