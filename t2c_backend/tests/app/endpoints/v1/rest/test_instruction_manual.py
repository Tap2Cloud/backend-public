import pytest
from fastapi.testclient import TestClient


# anchored ahead of the asset pass tests, not behind them: test_asset.py::test_list_asset_pass
# runs at the very end (after test_health.py) so it can read the documents of a finished
# asset pass, and anchoring this module behind it would close an ordering cycle
@pytest.mark.order(after="test_asset.py::test_update_asset_with_unauthenticated_client")
def test_get_list_of_instruction_manual(
    authenticated_client: TestClient,
):
    response = authenticated_client.get("api/v1/instruction-manual")

    assert response.status_code == 200


@pytest.mark.order(after="test_get_list_of_instruction_manual")
def test_get_list_of_instruction_manual_with_unauthorized_client(
    client: TestClient,
):
    response = client.get("api/v1/instruction-manual")

    assert response.status_code == 401


@pytest.mark.order(after="test_get_list_of_instruction_manual_with_unauthorized_client")
def test_get_list_of_instruction_manual_with_is_video_filter(
    authenticated_client: TestClient,
):
    response = authenticated_client.get(
        "api/v1/instruction-manual",
        params={
            "is_video": True,
        },
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_list_of_instruction_manual_with_is_video_filter")
def test_get_list_of_instruction_manual_with_is_document_filter(
    authenticated_client: TestClient,
):
    response = authenticated_client.get(
        "api/v1/instruction-manual",
        params={
            "is_document": True,
        },
    )

    assert response.status_code == 200


@pytest.mark.order(after="test_get_list_of_instruction_manual_with_is_document_filter")
def test_get_list_of_instruction_manual_with_is_document_and_is_video_filter(
    authenticated_client: TestClient,
):
    response = authenticated_client.get(
        "api/v1/instruction-manual",
        params={
            "is_document": True,
            "is_video": True,
        },
    )

    assert response.status_code == 200
