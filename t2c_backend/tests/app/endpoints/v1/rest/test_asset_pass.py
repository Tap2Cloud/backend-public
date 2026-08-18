import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(after="test_health.py::test_health")
def test_get_asset_pass_by_id(authenticated_client: TestClient, asset_pass_container):
    asset_pass_id = asset_pass_container["asset_pass"]["items"][0]["assetPass"]["passId"]
    response = authenticated_client.get(f"/8004/{asset_pass_id}")

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_pass_by_id")
def test_get_asset_pass_by_gtin_id(authenticated_client: TestClient, asset_pass_container):
    asset_pass_id = asset_pass_container["asset_pass"]["items"][0]["assetPass"]["passId"]
    gtin_id = asset_pass_container["asset_pass"]["items"][0]["assetType"]["gtin"]
    response = authenticated_client.get(f"/01/{gtin_id}/21/{asset_pass_id}")

    assert response.status_code == 200


@pytest.mark.order(after="test_get_asset_pass_by_gtin_id")
def test_get_asset_pass_by_invalid_id(authenticated_client: TestClient, asset_pass_container):
    asset_pass_id = asset_pass_container["asset_pass"]["items"][0]["assetPass"]["passId"]
    response = authenticated_client.get(f"/8004/{asset_pass_id + '100'}")

    assert response.status_code == 404


@pytest.mark.order(after="test_get_asset_pass_by_invalid_id")
def test_get_asset_pass_by_invalid_gtin_id(authenticated_client: TestClient, asset_pass_container):
    asset_pass_id = asset_pass_container["asset_pass"]["items"][0]["assetPass"]["passId"]
    gtin_id = asset_pass_container["asset_pass"]["items"][0]["assetType"]["gtin"]

    response = authenticated_client.get(f"/01/{gtin_id + '100'}/21/{asset_pass_id}")

    assert response.status_code == 400
