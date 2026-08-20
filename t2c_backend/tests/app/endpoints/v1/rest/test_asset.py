import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from utils.enums import AssetStatus, DocumentFor


@pytest.mark.order(after="test_asset_type.py::test_delete_asset_type_field_document")
def test_create_asset(
    authenticated_client: TestClient,
    fake: Faker,
    asset,
    asset_type_container,
    container,
    asset_pass_document_container,
):
    asset_type = next(
        assettype
        for assettype in asset_type_container["asset_types"]["items"]
        if assettype["name"] == asset_pass_document_container["asset_type_name"]
    )

    asset_pass_document_container[DocumentFor.InstructionManualDocuments]["id"] = next(
        document["id"]
        for document in asset_type["instructionManuals"]
        if document["name"]
        == asset_pass_document_container[DocumentFor.InstructionManualDocuments]["name"]
    )
    asset_pass_document_container[DocumentFor.AssetTypeFieldSpecificDocuments]["id"] = asset_type[
        "form"
    ][0]["values"]["id"]
    asset_pass_document_container["typeplate_id"] = asset_type["typeplates"]["id"]

    response = authenticated_client.post(
        "/api/v1/asset",
        json={
            **asset,
            "location": container["location"],
            "assetType": {
                "id": asset_type["id"],
                "name": asset_type["name"],
                "description": asset_type["description"],
            },
            "deviceId": f"{fake.uuid4()}",
            "status": random.choice(list(AssetStatus)),
        },
    )

    assert response.status_code == 201


@pytest.mark.order(after="test_create_asset")
def test_create_asset_for_second_user(
    authenticated_client: TestClient,
    fake: Faker,
    second_user_data,
    asset,
    asset_type_category_mapping_container,
    container,
):
    response = authenticated_client.post("/api/v1/login", json=second_user_data["credentials"])
    response = authenticated_client.post(
        "/api/v1/asset",
        json={
            **asset,
            "location": container["second_location"],
            "assetType": random.choice(
                random.choice(asset_type_category_mapping_container["asset_type_category"])[
                    "assetTypes"
                ]
            ),
            "status": random.choice(list(AssetStatus)),
        },
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )

    assert response.status_code == 201


@pytest.mark.order(after="test_create_asset_for_second_user")
def test_create_asset_with_unauthenticated_client(
    client: TestClient, asset, asset_type_container, asset_container, container
):
    asset["location"] = container["location"]["id"]
    asset["assetType"] = random.choice(
        [assettype["id"] for assettype in asset_type_container["asset_types"]["items"]]
    )
    asset["status"] = random.choice(list(AssetStatus))

    response = client.post("/api/v1/asset", json={**asset})

    assert response.status_code == 401


@pytest.mark.order(after="test_create_asset_with_unauthenticated_client")
def test_create_asset_with_fake_location(
    authenticated_client: TestClient,
    fake: Faker,
    asset,
    asset_type_category_mapping_container,
    asset_container,
    container,
):
    response = authenticated_client.post(
        "/api/v1/asset",
        json={
            **asset,
            "location": {**container["location"], "id": fake.random_int(max=8000000, min=4000)},
            "assetType": random.choice(
                random.choice(asset_type_category_mapping_container["asset_type_category"])[
                    "assetTypes"
                ]
            ),
            "status": random.choice(list(AssetStatus)),
        },
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_create_asset_with_fake_location")
def test_create_asset_with_fake_asset_type(
    authenticated_client: TestClient,
    fake: Faker,
    asset,
    asset_type_category_mapping_container,
    asset_container,
    container,
):
    asset = {
        **asset,
        "location": container["location"],
        "assetType": dict(
            random.choice(
                random.choice(asset_type_category_mapping_container["asset_type_category"])[
                    "assetTypes"
                ]
            )
        ),
        "status": random.choice(list(AssetStatus)),
    }

    asset["assetType"]["id"] = fake.random_int(max=8000000, min=4000)

    response = authenticated_client.post("/api/v1/asset", json={**asset})

    assert response.status_code == 404


@pytest.mark.order(after="test_create_asset_with_fake_asset_type")
def test_get_asset_with_unauthenticated_client(client: TestClient):
    response = client.put("/api/v1/asset", json={"categories": None, "status": None})

    assert response.status_code == 401


@pytest.mark.order(after="test_get_asset_with_unauthenticated_client")
def test_get_asset(authenticated_client: TestClient, asset_container):
    response = authenticated_client.put("/api/v1/asset", json={"categories": None, "status": None})
    asset_container["asset"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset")
def test_get_asset_with_filter_status(authenticated_client: TestClient, asset_container):
    response = authenticated_client.put(
        "/api/v1/asset",
        json={"categories": None, "status": [asset_container["asset"]["items"][0]["status"]]},
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["status"] == asset_container["asset"]["items"][0]["status"]


@pytest.mark.order(after="test_get_asset_with_filter_status")
def test_get_asset_with_filter_category(authenticated_client: TestClient, asset_container):
    category = asset_container["asset"]["items"][0]["assetType"]["assetTypeCategory"]

    response = authenticated_client.put(
        "/api/v1/asset", json={"categories": [category], "status": None}
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["assetType"]["assetTypeCategory"] == category


@pytest.mark.order(after="test_get_asset_with_filter_category")
def test_get_asset_with_query_asset_type_name(
    authenticated_client: TestClient, asset_type_container
):
    asset_type_name = random.choice(
        [assettype["name"] for assettype in asset_type_container["asset_types"]["items"]]
    )
    response = authenticated_client.put(
        f"/api/v1/asset/?q={asset_type_name}", json={"categories": None, "status": None}
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_with_query_asset_type_name")
def test_get_asset_with_query_serial_no(authenticated_client: TestClient, asset_container):
    serial_no = random.choice([assets["serialNo"] for assets in asset_container["asset"]["items"]])
    response = authenticated_client.put(
        f"/api/v1/asset/?q={serial_no}", json={"categories": None, "status": None}
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_with_query_serial_no")
def test_get_asset_with_query_serial_no_and_asset_type_name(
    authenticated_client: TestClient, asset_container, asset_type_container
):
    asset_type_name = random.choice(
        [assettype["name"] for assettype in asset_type_container["asset_types"]["items"]]
    )
    serial_no = random.choice([assets["serialNo"] for assets in asset_container["asset"]["items"]])
    response = authenticated_client.put(
        f"/api/v1/asset/?q={serial_no}&q={asset_type_name}",
        json={"categories": None, "status": None},
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_with_query_serial_no_and_asset_type_name")
def test_get_asset_by_id(authenticated_client: TestClient, asset_container):
    asset_id = asset_container["asset"]["items"][0]["id"]
    response = authenticated_client.get(f"/api/v1/asset/{asset_id}")
    asset_container["asset_to_update"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_by_id")
def test_get_asset_by_invalid_id(authenticated_client: TestClient, asset_container):
    asset_id = asset_container["asset"]["items"][0]["id"]
    response = authenticated_client.get(f"/api/v1/asset/{asset_id + 9999999}")
    assert response.status_code == 404


@pytest.mark.order(after="test_get_asset_by_invalid_id")
def test_get_asset_by_unauthenticated_client(client: TestClient, asset_container):
    asset_id = asset_container["asset"]["items"][0]["id"]
    response = client.get(f"/api/v1/asset/{asset_id}")

    assert response.status_code == 401


@pytest.mark.order(after="test_get_asset_by_unauthenticated_client")
def test_update_asset(authenticated_client: TestClient, asset_container, update_asset):
    asset_id = asset_container["asset_to_update"]["id"]

    response = authenticated_client.put(
        f"/api/v1/asset/{asset_id}",
        json={
            **update_asset,
        },
    )
    assert response.status_code == 200
    assert update_asset["status"] != asset_container["asset_to_update"]["status"]
    assert update_asset["serialNo"] != asset_container["asset_to_update"]["serialNo"]
    assert (
        update_asset["economicOperator"] != asset_container["asset_to_update"]["economicOperator"]
    )


@pytest.mark.order(after="test_update_asset")
def test_update_asset_with_invalid_id(
    authenticated_client: TestClient, asset_container, update_asset
):
    asset_id = asset_container["asset_to_update"]["id"]

    response = authenticated_client.put(
        f"/api/v1/asset/{asset_id + 1000}",
        json={
            **update_asset,
        },
    )
    assert response.status_code == 404


@pytest.mark.order(after="test_update_asset_with_invalid_id")
def test_update_asset_with_unauthenticated_client(
    client: TestClient, asset_container, update_asset
):
    asset_id = asset_container["asset_to_update"]["id"]

    response = client.put(
        f"/api/v1/asset/{asset_id}",
        json={
            **update_asset,
        },
    )
    assert response.status_code == 401


@pytest.mark.order(after="test_health.py::test_health")
def test_list_asset_pass(authenticated_client: TestClient, asset_pass_document_container):
    response = authenticated_client.get("/api/v1/asset-pass")

    asset_type_name = asset_pass_document_container["asset_type_name"]
    asset_pass = next(
        item
        for item in response.json()["items"]
        if item["assetPass"]["assetType"]["name"] == asset_type_name
    )

    eu_file = asset_pass["assetType"]["typeplates"]["euFile"]
    asset_pass_document_container[DocumentFor.EuFiles]["id"] = eu_file["id"]

    asset_pass_document_container["pass_id"] = asset_pass["assetPass"]["passId"]

    assert eu_file["name"] == asset_pass_document_container[DocumentFor.EuFiles]["name"]

    assert response.status_code == 200


@pytest.mark.order(after="test_list_asset_pass")
def test_list_asset_pass_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/asset-pass")

    assert response.status_code == 401


@pytest.mark.order(after="test_list_asset_pass_with_unauthenticated_client")
def test_get_asset_pass_instruction_manual_document(
    public_client: TestClient, asset_pass_document_container
):
    document = asset_pass_document_container[DocumentFor.InstructionManualDocuments]

    response = public_client.get(
        f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
        f"/document/{DocumentFor.InstructionManualDocuments}/{document['id']}"
    )

    assert response.status_code == 200
    assert response.content == document["content"]
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == f'inline; filename="{document["name"]}"'


@pytest.mark.order(after="test_get_asset_pass_instruction_manual_document")
def test_get_asset_pass_eu_file_document(public_client: TestClient, asset_pass_document_container):
    document = asset_pass_document_container[DocumentFor.EuFiles]

    response = public_client.get(
        f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
        f"/document/{DocumentFor.EuFiles}/{document['id']}"
    )

    assert response.status_code == 200
    assert response.content == document["content"]
    assert response.headers["content-disposition"] == f'inline; filename="{document["name"]}"'


@pytest.mark.order(after="test_get_asset_pass_eu_file_document")
def test_get_asset_pass_audit_task_document(
    public_client: TestClient, asset_pass_document_container
):
    document = asset_pass_document_container[DocumentFor.AuditTaskDocuments]

    response = public_client.get(
        f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
        f"/document/{DocumentFor.AuditTaskDocuments}/{document['id']}"
    )

    assert response.status_code == 200
    assert response.content == document["content"]
    assert response.headers["content-disposition"] == f'inline; filename="{document["name"]}"'


@pytest.mark.order(after="test_get_asset_pass_audit_task_document")
def test_get_asset_pass_field_specific_document(
    public_client: TestClient, asset_pass_document_container
):
    document = asset_pass_document_container[DocumentFor.AssetTypeFieldSpecificDocuments]

    response = public_client.get(
        f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
        f"/document/{DocumentFor.AssetTypeFieldSpecificDocuments}/{document['id']}"
    )

    assert response.status_code == 200
    assert response.content == document["content"]
    # a field document has no stored content type, it is guessed from the file name
    assert response.headers["content-type"] == "image/png"
    assert response.headers["content-disposition"] == f'inline; filename="{document["name"]}"'


@pytest.mark.order(after="test_get_asset_pass_field_specific_document")
def test_download_asset_pass_document_as_attachment(
    public_client: TestClient, asset_pass_document_container
):
    document = asset_pass_document_container[DocumentFor.InstructionManualDocuments]

    response = public_client.get(
        f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
        f"/document/{DocumentFor.InstructionManualDocuments}/{document['id']}",
        params={"download": True},
    )

    assert response.status_code == 200
    assert response.content == document["content"]
    assert response.headers["content-disposition"] == f'attachment; filename="{document["name"]}"'


@pytest.mark.order(after="test_download_asset_pass_document_as_attachment")
def test_get_asset_pass_document_with_fake_pass_id(
    public_client: TestClient, fake: Faker, asset_pass_document_container
):
    document = asset_pass_document_container[DocumentFor.InstructionManualDocuments]

    response = public_client.get(
        f"/api/v1/asset-pass/{fake.lexify(text='????????????')}"
        f"/document/{DocumentFor.InstructionManualDocuments}/{document['id']}"
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_get_asset_pass_document_with_fake_pass_id")
def test_get_asset_pass_document_with_fake_document_id(
    public_client: TestClient, fake: Faker, asset_pass_document_container
):
    for document_for in DocumentFor:
        response = public_client.get(
            f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
            f"/document/{document_for}/{fake.uuid4()}"
        )

        assert response.status_code == 404, document_for


@pytest.mark.order(after="test_get_asset_pass_document_with_fake_document_id")
def test_get_asset_pass_document_from_another_document_source(
    public_client: TestClient, asset_pass_document_container
):
    for document_for in DocumentFor:
        for other_document_for in DocumentFor:
            if other_document_for == document_for:
                continue

            response = public_client.get(
                f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
                f"/document/{other_document_for}"
                f"/{asset_pass_document_container[document_for]['id']}"
            )

            assert response.status_code == 404, (document_for, other_document_for)


@pytest.mark.order(after="test_get_asset_pass_document_from_another_document_source")
def test_get_asset_pass_document_with_invalid_document_for(
    public_client: TestClient, fake: Faker, asset_pass_document_container
):
    document = asset_pass_document_container[DocumentFor.InstructionManualDocuments]

    response = public_client.get(
        f"/api/v1/asset-pass/{asset_pass_document_container['pass_id']}"
        f"/document/{fake.word()}/{document['id']}"
    )

    assert response.status_code == 422
