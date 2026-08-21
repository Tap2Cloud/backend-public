import json
import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient


@pytest.mark.order(
    after="test_typeplate.py::test_delete_typeplate_document_with_fake_typeplate_id",
)
def test_create_audit_task1_with_document(
    audit_task,
    audit_task_container,
    authenticated_client: TestClient,
    fake: Faker,
):
    fake_file = f"{fake.file_name()}.png"
    document_content = fake.text().encode("utf-8")

    response = authenticated_client.post(
        "/api/v1/audit/task",
        data={"task": json.dumps(audit_task)},
        files=[("documents", (fake_file, document_content, "image/png"))],
    )

    audit_task_container.append(response.json())

    assert response.status_code == 201


@pytest.mark.order(after="test_create_audit_task1_with_document")
def test_create_audit_task2_without_document(
    audit_task,
    audit_task_container,
    authenticated_client: TestClient,
    fake: Faker,
):
    response = authenticated_client.post(
        "/api/v1/audit/task",
        data={"task": json.dumps(audit_task)},
    )

    audit_task_container.append(response.json())

    assert response.status_code == 201


@pytest.mark.order(after="test_create_audit_task2_without_document")
def test_create_audit_task_with_document_and_without_task_name(
    audit_task,
    audit_task_container,
    authenticated_client: TestClient,
    fake: Faker,
):
    fake_file = fake.file_name()
    document_content = fake.text().encode("utf-8")

    response = authenticated_client.post(
        "/api/v1/audit/task",
        files=[("document", (fake_file, document_content, "application/pdf"))],
    )

    assert response.status_code == 422


@pytest.mark.order(after="test_create_audit_task_with_document_and_without_task_name")
def test_create_audit_task_with_unauthenticated_client(client: TestClient, audit_task):
    response = client.post(
        "/api/v1/audit/task",
        data={"task": json.dumps(audit_task)},
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_create_audit_task_with_unauthenticated_client")
def test_create_audit(
    authenticated_client: TestClient, audit, audit_task_container, asset_container, audit_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])

    audit_container.append({"asset_id": asset_id})
    response = authenticated_client.post(
        f"/api/v1/asset/{asset_id}/audit", json={**audit, "auditTasks": audit_task_container}
    )

    audit_container.append(response.json())
    assert response.status_code == 201


@pytest.mark.order(after="test_create_audit")
def test_create_audit_without_audit_task(
    authenticated_client: TestClient, audit, audit_task_container, asset_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])

    response = authenticated_client.post(f"/api/v1/asset/{asset_id}/audit", json={**audit})

    assert response.status_code == 400


@pytest.mark.order(after="test_create_audit_without_audit_task")
def test_create_audit_with_audit_task_only(
    authenticated_client: TestClient, audit, audit_task_container, asset_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])

    response = authenticated_client.post(
        f"/api/v1/asset/{asset_id}/audit", json={"auditTask": audit_task_container}
    )

    assert response.status_code == 422


@pytest.mark.order(after="test_service.py::test_delete_service_with_invalid_id")
def test_create_audit_with_invalid_value(
    authenticated_client: TestClient, audit, audit_task_container, asset_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])
    audit["validUntil"] = audit["inspectionDate"]
    response = authenticated_client.post(
        f"/api/v1/asset/{asset_id}/audit", json={"auditTask": audit_task_container, **audit}
    )

    assert response.status_code == 400


@pytest.mark.order(after="test_create_audit_with_audit_task_only")
def test_create_audit_with_unauthenticated_client(
    client: TestClient, audit, audit_task_container, asset_container
):
    asset_id = random.choice([assets["id"] for assets in asset_container["asset"]["items"]])

    response = client.post(
        f"/api/v1/asset/{asset_id}/audit", json={**audit, "auditTask": audit_task_container}
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_create_audit_with_unauthenticated_client")
def test_create_audit_with_fake_asset_id(
    authenticated_client: TestClient, audit, audit_task_container, fake: Faker
):
    asset_id = fake.random_int(max=8000000, min=4000)

    response = authenticated_client.post(
        f"/api/v1/asset/{asset_id}/audit", json={**audit, "auditTask": audit_task_container}
    )

    assert response.status_code == 404


@pytest.mark.order(after="test_create_audit_with_fake_asset_id")
def test_get_audit(authenticated_client: TestClient):
    response = authenticated_client.get("/api/v1/audit")

    assert response.status_code == 200


@pytest.mark.order(after="test_get_audit")
def test_get_audit_with_query_serial_no(authenticated_client: TestClient, asset_container):
    serial_no = random.choice([assets["serialNo"] for assets in asset_container["asset"]["items"]])
    response = authenticated_client.get(f"/api/v1/audit?q={serial_no}")

    assert response.status_code == 200


@pytest.mark.order(after="test_get_audit_with_query_serial_no")
def test_get_audit_with_query_asset_type_name(
    authenticated_client: TestClient, asset_type_container
):
    asset_type_name = random.choice(
        [assettype["name"] for assettype in asset_type_container["asset_types"]["items"]]
    )
    response = authenticated_client.get(f"/api/v1/audit?q={asset_type_name}")

    assert response.status_code == 200


@pytest.mark.order(after="test_get_audit_with_query_asset_type_name")
def test_get_audit_with_inspection_date_filter(authenticated_client: TestClient, fake: Faker):
    start_date = fake.date_between(start_date="-30d", end_date="-5d")
    end_date = fake.date_between(start_date=start_date, end_date="today")

    response = authenticated_client.get(
        "/api/v1/audit",
        params={
            "inspection_start_date": start_date.isoformat(),
            "inspection_end_date": end_date.isoformat(),
        },
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_audit_with_inspection_date_filter")
def test_get_audit_with_valid_until_filter(authenticated_client: TestClient, fake: Faker):
    valid_start_date = fake.date_between(start_date="+1d", end_date="+30d")
    valid_end_date = fake.date_between(start_date=valid_start_date, end_date="+60d")

    response = authenticated_client.get(
        "/api/v1/audit",
        params={
            "valid_until_start_date": valid_start_date.isoformat(),
            "valid_until_end_date": valid_end_date.isoformat(),
        },
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_audit_with_valid_until_filter")
def test_get_audit_with_is_audit_filter(authenticated_client: TestClient, fake: Faker):
    response = authenticated_client.get(
        "/api/v1/audit",
        params={
            "is_audit_available": True,
        },
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_audit_with_is_audit_filter")
def test_get_audit_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/audit")

    assert response.status_code == 401


@pytest.mark.order(after="test_get_audit_with_unauthenticated_client")
def test_download_audit_document(authenticated_client: TestClient, audit_container):
    audit = audit_container[1]
    audit_id = audit.get("id")
    audit_task_id = audit.get("auditTasks", [{}])[0].get("id")
    document_id = audit.get("auditTasks", [{}])[0].get("documents")[0].get("id")
    response = authenticated_client.get(
        f"/api/v1/audit/{audit_id}/task/{audit_task_id}/document/{document_id}/get"
    )
    assert response.status_code == 200


@pytest.mark.order(after="test_download_audit_document")
def test_generate_audit_report(authenticated_client: TestClient, audit_container):
    audit_id = audit_container[1].get("id")
    asset_id = audit_container[0].get("asset_id")

    response = authenticated_client.get(
        f"/api/v1/asset/{asset_id}/audit/{audit_id}/audit-report", headers={"Accept-Language": "en"}
    )

    assert response.status_code == 200
