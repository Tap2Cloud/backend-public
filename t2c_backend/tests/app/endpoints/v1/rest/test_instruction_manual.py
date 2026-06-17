import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(100)
def test_get_list_of_instruction_manual(
    authenticated_client: TestClient,
):
    response = authenticated_client.get("api/v1/instruction-manual")

    assert response.status_code == 200


@pytest.mark.order(101)
def test_get_list_of_instruction_manual_with_unauthorized_client(
    client: TestClient,
):
    response = client.get("api/v1/instruction-manual")

    assert response.status_code == 401


@pytest.mark.order(102)
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


@pytest.mark.order(103)
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


@pytest.mark.order(104)
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
