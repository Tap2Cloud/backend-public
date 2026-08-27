import pytest
from faker import Faker
from fastapi.testclient import TestClient
from utils.enums import DocumentFor


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
