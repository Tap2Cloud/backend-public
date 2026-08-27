import json
import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from utils.enums import DocumentFor


@pytest.mark.order(
    after="test_asset_type_category.py::test_asset_type_category_with_invalid_group_id",
)
def test_create_asset_type_string(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    fake_file = fake.file_name()
    document_content = fake.text().encode("utf-8")

    asset_type_field["responseValue"] = fake.name()
    for field in container["string_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["string_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }
    files = [
        ("instruction_manuals", (fake_file, document_content, "text/plain")),
    ]
    if container["string_asset_type_category"]["hasTypeplates"]:
        files.append(("eu_file", (fake_file, document_content, "text/plain")))

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
        files=files,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_string")
def test_create_asset_type_string_for_second_user(
    second_user_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type_field["responseValue"] = fake.name()
    for field in container["second_string_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["second_string_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = second_user_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_asset_type_category.py::test_get_asset_type_category_mapping")
def test_create_asset_type_integer(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.random_int()}"
    for field in container["integer_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["integer_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_integer")
def test_create_asset_type_time(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.time()}"
    for field in container["time_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["time_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_time")
def test_create_asset_type_url(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.url()}"
    for field in container["url_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["url_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_url")
def test_create_asset_type_password(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.password()}"
    for field in container["password_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["password_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_password")
def test_create_asset_type_image(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
    asset_pass_document_container,
):
    fake_file = f"image-custom-field-{fake.random_int()}.png"
    document_content = fake.text().encode("utf-8")
    instruction_manual = f"image-instruction-manual-{fake.random_int()}.pdf"
    instruction_manual_content = fake.text().encode("utf-8")

    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake_file}"
    for field in container["image_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["image_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
        files=[
            ("custom_media_fields", (fake_file, document_content, "image/png")),
            (
                "instruction_manuals",
                (instruction_manual, instruction_manual_content, "application/pdf"),
            ),
        ],
    )

    asset_pass_document_container.update(
        {
            "asset_type_name": asset_type["name"],
            DocumentFor.AssetTypeFieldSpecificDocuments: {
                "name": fake_file,
                "content": document_content,
            },
            DocumentFor.InstructionManualDocuments: {
                "name": instruction_manual,
                "content": instruction_manual_content,
            },
        }
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_image")
def test_create_asset_type_file(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    fake_file = fake.file_name()
    document_content = fake.text().encode("utf-8")

    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = fake_file
    for field in container["file_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["file_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
        files=[("custom_media_fields", (fake_file, document_content, "text/plain"))],
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_file")
def test_create_asset_type_email(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.email()}"
    for field in container["email_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["email_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_email")
def test_create_asset_type_date(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.date()}"
    for field in container["date_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["date_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_date")
def test_create_asset_type_datetime(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.date_time()}"
    for field in container["datetime_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["datetime_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_datetime")
def test_create_asset_type_radio(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    asset_type_field_options,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = ""
    for field in container["radio_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]
        for asset_type_option in asset_type_field_options:
            asset_type_option["optionId"] = random.choice(
                [option["id"] for option in field["options"]]
            )

    asset_type_field["assetTypeFieldOptions"] = asset_type_field_options

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["radio_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_radio")
def test_create_asset_type_multiselect(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    asset_type_field_options,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = fake.name()
    for field in container["multiselect_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]
        for asset_type_option in asset_type_field_options:
            asset_type_option["optionId"] = random.choice(
                [option["id"] for option in field["options"]]
            )
    asset_type_field["assetTypeFieldOptions"] = asset_type_field_options

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["multiselect_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_multiselect")
def test_create_asset_type_checkbox(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    asset_type_field_options,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = fake.name()
    for field in container["checkbox_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]
        for asset_type_option in asset_type_field_options:
            asset_type_option["optionId"] = random.choice(
                [option["id"] for option in field["options"]]
            )
    asset_type_field["assetTypeFieldOptions"] = asset_type_field_options

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["checkbox_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_checkbox")
def test_create_asset_type_select(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    asset_type_field_options,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = fake.name()
    for field in container["select_type_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]
        for asset_type_option in asset_type_field_options:
            asset_type_option["optionId"] = random.choice(
                [option["id"] for option in field["options"]]
            )
    asset_type_field["assetTypeFieldOptions"] = asset_type_field_options

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["select_type_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 204


@pytest.mark.order(after="test_create_asset_type_select")
def test_create_asset_type_with_unauthenticated_client(
    client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type["name"] = fake.name()
    asset_type_field["responseValue"] = f"{fake.random_int()}"
    for field in container["integer_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["string_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_create_asset_type_with_unauthenticated_client")
def test_create_asset_type_with_false_typeplate_image(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type,
    asset_type_field,
    container,
    typeplate_details,
):
    asset_type_field["responseValue"] = fake.name()
    for field in container["string_asset_type_category"]["fields"]:
        asset_type_field["fieldId"] = field["id"]

    asset_type_data = {
        "name": asset_type["name"],
        "videoTitle": asset_type["videoTitle"],
        "videoLinks": asset_type["videoLinks"],
        "webLink": asset_type["webLink"],
        "webLinkTitle": asset_type["webLinkTitle"],
        "description": asset_type["description"],
        "weight": asset_type["weight"],
        "manufacturer": asset_type["manufacturer"],
        "assetTypeCategoryId": container["string_asset_type_category"]["id"],
        "fields": [asset_type_field],
        "typeplate_images": [{"id": "598f366d-5f24-4a08-ba30-afb411fb4c5e"}],
        "typeplateDetails": typeplate_details,
    }

    form_data = {
        "asset_type_data": json.dumps(asset_type_data),
    }

    response = authenticated_client.post(
        "/api/v1/asset-type",
        data=form_data,
    )

    assert response.status_code == 422


@pytest.mark.order(after="test_create_asset_type_with_false_typeplate_image")
def test_list_asset_type_with_unauthenticated_client(
    client: TestClient,
):
    response = client.put("/api/v1/asset-type", json={"categories": None})

    assert response.status_code == 401


@pytest.mark.order(after="test_list_asset_type_with_unauthenticated_client")
def test_list_asset_type_with_authenticated_client(
    authenticated_client: TestClient,
    asset_type_container,
):
    response = authenticated_client.put("/api/v1/asset-type?pageSize=20", json={"categories": None})
    asset_type_container["asset_types"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_list_asset_type_with_authenticated_client")
def test_list_asset_type_with_query(authenticated_client: TestClient, asset_type_container):
    asset_type_name = random.choice(asset_type_container["asset_types"]["items"])
    response = authenticated_client.put(
        f"api/v1/asset-type?query={asset_type_name['name']}", json={"categories": None}
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_list_asset_type_with_query")
def test_list_asset_type_filter_by_category(
    authenticated_client: TestClient, asset_type_category_detail_container
):
    category = random.choice(asset_type_category_detail_container["asset_type_category"])
    response = authenticated_client.put("api/v1/asset-type", json={"categories": [category]})
    assert response.status_code == 200
    assert response.json()["items"][0]["assetTypeCategory"] == category


@pytest.mark.order(after="test_list_asset_type_filter_by_category")
def test_upload_asset_type_document(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_with_documents_container,
    asset_type_container,
):
    asset_type_id = random.choice(
        [assettype["id"] for assettype in asset_type_container["asset_types"]["items"]]
    )

    fake_file = fake.file_name(category="document", extension="pdf")
    document_content = fake.text().encode("utf-8")

    response = authenticated_client.post(
        f"api/v1/asset-type/{asset_type_id}/documents",
        files=[("documents", (str(fake_file), document_content, "application/pdf"))],
    )

    asset_type_with_documents_container.update(
        {"asset_type_id": asset_type_id, "document_name": fake_file}
    )

    assert response.status_code == 201


@pytest.mark.order(after="test_upload_asset_type_document")
def test_upload_asset_type_documents(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_with_documents_container,
    asset_type_container,
):
    asset_type_id = asset_type_with_documents_container["asset_type_id"]

    fake_file1 = fake.file_name(category="document", extension="pdf")
    document_content1 = fake.text().encode("utf-8")

    fake_file2 = fake.file_name(category="document", extension="pdf")
    document_content2 = fake.text().encode("utf-8")

    fake_file3 = fake.file_name(category="document", extension="pdf")
    document_content3 = fake.text().encode("utf-8")

    response = authenticated_client.post(
        f"api/v1/asset-type/{asset_type_id}/documents",
        files=[
            ("documents", (fake_file1, document_content1, "application/pdf")),
            ("documents", (fake_file2, document_content2, "application/pdf")),
            ("documents", (fake_file3, document_content3, "application/pdf")),
        ],
    )

    assert response.status_code == 201


@pytest.mark.order(after="test_upload_asset_type_documents")
def test_upload_asset_type_document_with_unauthenticated_client(
    client: TestClient,
    fake: Faker,
    asset_type_container,
):
    fake_file = fake.file_name()
    document_content = fake.text().encode("utf-8")

    asset_type_id = random.choice(
        [assettype["id"] for assettype in asset_type_container["asset_types"]["items"]]
    )

    response = client.post(
        f"api/v1/asset-type/{asset_type_id}/documents",
        files=[("documents", (fake_file, document_content, "application/pdf"))],
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_upload_asset_type_document_with_unauthenticated_client")
def test_upload_asset_type_document_with_fake_asset_type_id(
    authenticated_client: TestClient,
    fake: Faker,
    asset_type_container,
):
    fake_file = fake.file_name()
    document_content = fake.text().encode("utf-8")

    asset_type_id = fake.random_int(max=8000000, min=4000)

    response = authenticated_client.post(
        f"api/v1/asset-type/{asset_type_id}/documents",
        files=[("documents", (fake_file, document_content, "application/pdf"))],
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_upload_asset_type_document_with_fake_asset_type_id")
def test_upload_asset_type_field_document(
    authenticated_client: TestClient,
    asset_type_container,
    fake: Faker,
    asset_type_with_documents_container,
):
    asset_type = [
        assettype
        for assettype in asset_type_container["asset_types"]["items"]
        if assettype["form"][0]["fields"]["fieldType"] == "file"
    ][0]

    fake_file = fake.file_name(category="document", extension="pdf")
    document_content = fake.text().encode("utf-8")

    response = authenticated_client.post(
        f"api/v1/asset-type/{asset_type['id']}/custom-field/documents",
        data={"customFieldId": asset_type["form"][0]["fields"]["id"]},
        files=[("documents", (str(fake_file), document_content, "application/pdf"))],
    )

    asset_type_with_documents_container.update({"media_field": response.json()})
    assert response.status_code == 201


@pytest.mark.order(after="test_upload_asset_type_field_document")
def test_upload_asset_type_field_document_with_unauthenticated_client(
    client: TestClient,
    asset_type_container,
    fake: Faker,
    asset_type_with_documents_container,
):
    asset_type = [
        assettype
        for assettype in asset_type_container["asset_types"]["items"]
        if assettype["form"][0]["fields"]["fieldType"] == "file"
    ][0]

    fake_file = fake.file_name(category="document", extension="pdf")
    document_content = fake.text().encode("utf-8")

    response = client.post(
        f"api/v1/asset-type/{asset_type['id']}/custom-field/documents",
        data={"customFieldId": asset_type["form"][0]["fields"]["id"]},
        files=[("documents", (str(fake_file), document_content, "application/pdf"))],
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_upload_asset_type_field_document_with_unauthenticated_client")
def test_upload_asset_type_field_document_with_invalid_filed_id(
    authenticated_client: TestClient,
    asset_type_container,
    fake: Faker,
    asset_type_with_documents_container,
):
    asset_type = [
        assettype
        for assettype in asset_type_container["asset_types"]["items"]
        if assettype["form"][0]["fields"]["fieldType"] == "file"
    ][0]

    fake_file = fake.file_name(category="document", extension="pdf")
    document_content = fake.text().encode("utf-8")

    response = authenticated_client.post(
        f"api/v1/asset-type/{asset_type['id']}/custom-field/documents",
        data={"customFieldId": asset_type["form"][0]["fields"]["id"] + 10000},
        files=[("documents", (str(fake_file), document_content, "application/pdf"))],
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_upload_asset_type_field_document_with_invalid_filed_id")
def test_get_asset_type_by_id(
    authenticated_client: TestClient,
    asset_type_with_documents_container,
):
    response = authenticated_client.get(
        f"api/v1/asset-type/{asset_type_with_documents_container['asset_type_id']}"
    )
    asset_type_with_documents_container.update({"asset_type_document": response.json()})
    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_type_by_id")
def test_get_asset_type_by_id_with_unauthenticated_client(
    client: TestClient,
    asset_type_with_documents_container,
):
    response = client.get(
        f"api/v1/asset-type/{asset_type_with_documents_container['asset_type_id']}"
    )
    assert response.status_code == 401


@pytest.mark.order(after="test_get_asset_type_by_id_with_unauthenticated_client")
def test_get_asset_type_with_invalid_id(
    authenticated_client: TestClient,
):
    response = authenticated_client.get("api/v1/asset-type/-1")
    assert response.status_code == 404


@pytest.mark.order(after="test_get_asset_type_with_invalid_id")
def test_get_asset_type_document(
    authenticated_client: TestClient,
    asset_type_with_documents_container,
):
    doc = asset_type_with_documents_container["asset_type_document"]["instructionManuals"][0]
    url = (
        f"/api/v1/asset-type/{asset_type_with_documents_container['asset_type_document']['id']}/"
        f"get/document/{doc['id']}/{doc['name']}"
    )

    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_type_document")
def test_get_asset_type_document_with_unauthenticated_client(
    client: TestClient,
    asset_type_with_documents_container,
):
    doc = asset_type_with_documents_container["asset_type_document"]["instructionManuals"][-1]
    url = (
        f"/api/v1/asset-type/{asset_type_with_documents_container['asset_type_document']['id']}/"
        f"get/document/{doc['id']}/{doc['name']}"
    )
    response = client.get(url)
    assert response.status_code == 401


@pytest.mark.order(after="test_get_asset_type_document_with_unauthenticated_client")
def test_get_asset_type_document_with_invalid_document_id(
    authenticated_client: TestClient,
    asset_type_with_documents_container,
):
    doc = asset_type_with_documents_container["asset_type_document"]["instructionManuals"][-1]
    url = (
        f"/api/v1/asset-type/{asset_type_with_documents_container['asset_type_document']['id']}/"
        f"get/document/{doc['id'].replace('a', 'b')}/{doc['name']}"
    )

    with pytest.raises(FileNotFoundError):
        response = authenticated_client.get(url)
        assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_type_document_with_invalid_document_id")
def test_get_asset_type_field_document(
    authenticated_client: TestClient,
    asset_type_with_documents_container,
):
    doc = asset_type_with_documents_container["media_field"]["form"][0]["values"]
    url = (
        f"/api/v1/asset-type/{asset_type_with_documents_container['media_field']['id']}/"
        f"get/custom-field/document/{doc['id']}/{doc['responseValue']}"
    )

    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_type_field_document")
def test_get_asset_type_field_document_with_unauthenticated_client(
    client: TestClient,
    asset_type_with_documents_container,
):
    doc = asset_type_with_documents_container["media_field"]["form"][0]["values"]
    url = (
        f"/api/v1/asset-type/{asset_type_with_documents_container['media_field']['id']}/"
        f"get/custom-field/document/{doc['id']}/{doc['responseValue']}"
    )
    response = client.get(url)
    assert response.status_code == 401


@pytest.mark.order(after="test_get_asset_type_field_document_with_unauthenticated_client")
def test_get_asset_type_field_document_with_invalid_id(
    authenticated_client: TestClient,
    asset_type_with_documents_container,
):
    doc = asset_type_with_documents_container["media_field"]["form"][0]["values"]
    url = (
        f"/api/v1/asset-type/{asset_type_with_documents_container['media_field']['id']}/"
        f"get/custom-field/document/{doc['id'] + 10000}/{doc['responseValue']}"
    )
    with pytest.raises(FileNotFoundError):
        response = authenticated_client.get(url)
        assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_type_field_document_with_invalid_id")
def test_update_asset_type(
    authenticated_client: TestClient, asset_type_with_documents_container, updated_asset_type
):
    field_values = [
        field["values"]
        for field in asset_type_with_documents_container["asset_type_document"]["form"]
    ]
    updated_asset_type = {
        **updated_asset_type,
        "fields": field_values,
    }
    response = authenticated_client.put(
        f"/api/v1/asset-type/{asset_type_with_documents_container['asset_type_document']['id']}",
        json=updated_asset_type,
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_update_asset_type")
def test_update_asset_type_with_unauthenticated_client(
    client: TestClient, asset_type_with_documents_container, updated_asset_type
):
    field_values = [
        field["values"]
        for field in asset_type_with_documents_container["asset_type_document"]["form"]
    ]
    updated_asset_type = {
        **updated_asset_type,
        "fields": field_values,
    }
    response = client.put(
        f"/api/v1/asset-type/{asset_type_with_documents_container['asset_type_document']['id']}",
        json=updated_asset_type,
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_update_asset_type_with_unauthenticated_client")
def test_update_asset_type_with_invalid_id(
    authenticated_client: TestClient, asset_type_with_documents_container, updated_asset_type
):
    field_values = [
        field["values"]
        for field in asset_type_with_documents_container["asset_type_document"]["form"]
    ]
    updated_asset_type = {
        **updated_asset_type,
        "fields": field_values,
    }
    response = authenticated_client.put(
        "/api/v1/asset-type/-1",
        json=updated_asset_type,
    )

    assert response.status_code == 404


# TODO : Payload not working with delete method
# @pytest.mark.order(104)
# def test_delete_asset_type_document(
#     authenticated_client: TestClient,
#     asset_type_with_documents_container,
# ):
#     doc = asset_type_with_documents_container["asset_type_document"]["instructionManuals"][-1]
#     url = (
#         f"/api/v1/instruction-manual
#         /{asset_type_with_documents_container['asset_type_document']['id']}"
#     )
#
#     response = authenticated_client.delete(
#         url,
#         json=json.dumps([{"instructionManualId": doc['id']}])
#     )
#     assert response.status_code == 204


@pytest.mark.order(after="test_update_asset_type_with_invalid_id")
def test_delete_asset_type_field_document(
    authenticated_client: TestClient, asset_type_with_documents_container
):
    doc = asset_type_with_documents_container["media_field"]["form"][0]["values"]
    url = (
        f"/api/v1/asset-type/custom-field/{asset_type_with_documents_container['media_field']['id']}/"
        f"{doc['id']}"
    )
    response = authenticated_client.delete(url)
    assert response.status_code == 204
