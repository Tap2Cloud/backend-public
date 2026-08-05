import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(after="test_audit.py::test_create_audit_with_invalid_value")
def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
