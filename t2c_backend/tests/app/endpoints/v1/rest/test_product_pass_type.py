import pytest
from fastapi.testclient import TestClient


@pytest.mark.order(after="test_authentication.py::test_authentication_without_password")
def test_get_product_pass_type(authenticated_client: TestClient, product_pass_type_container):
    response = authenticated_client.get("/api/v1/product-pass-type")

    product_pass_type_container["product_pass_types"] = response.json()

    assert response.status_code == 200
