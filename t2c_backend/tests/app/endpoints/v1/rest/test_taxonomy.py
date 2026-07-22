import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(5)
def test_get_taxonomy(authenticated_client: TestClient, taxonomy_container):
    response = authenticated_client.get("/api/v1/taxonomies")

    taxonomy_container["taxonomies"] = response.json()

    assert response.status_code == 200
