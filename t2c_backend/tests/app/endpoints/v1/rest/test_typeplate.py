import json
import random

import pytest
from faker import Faker
from fastapi.testclient import TestClient


@pytest.mark.order(116)
def test_list_typeplate(authenticated_client: TestClient, typeplate_container):
    response = authenticated_client.get("/api/v1/typeplate")
    typeplate_container["typeplate"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(117)
def test_list_typeplate_with_unauthenticated_client(client: TestClient):
    response = client.get("/api/v1/typeplate")

    assert response.status_code == 401


@pytest.mark.order(118)
def test_list_typeplate_with_query_asset_type_name(
    authenticated_client: TestClient, asset_type_container
):
    asset_type_name = random.choice(
        [assettype["name"] for assettype in asset_type_container["asset_types"]["items"]]
    )
    response = authenticated_client.get(f"/api/v1/typeplate?q={asset_type_name}")

    assert response.status_code == 200


@pytest.mark.order(119)
def test_list_typeplate_with_query_asset_type_category_name(
    authenticated_client: TestClient, asset_type_category_detail_container
):
    asset_type_category_name = random.choice(
        [
            category["name"]
            for category in asset_type_category_detail_container["asset_type_category"]
        ]
    )
    response = authenticated_client.get(f"/api/v1/typeplate?q={asset_type_category_name}")

    assert response.status_code == 200


@pytest.mark.order(120)
def test_list_typeplate_with_typeplate_created_filter(
    authenticated_client: TestClient, fake: Faker
):
    start_date = fake.date_between(start_date="-30d", end_date="-5d")
    end_date = fake.date_between(start_date=start_date, end_date="today")

    response = authenticated_client.get(
        "/api/v1/typeplate",
        params={
            "typeplate_created_start_date": start_date.isoformat(),
            "typeplate_created_end_date": end_date.isoformat(),
        },
    )

    assert response.status_code == 200


@pytest.mark.order(126)
def test_get_typeplate_by_id(authenticated_client: TestClient, typeplate_container):
    if len(typeplate_container["typeplate"]["items"]) <= 0:
        assert True
    else:
        typeplate_id = random.choice(
            [
                typeplate["typeplateDetails"]["id"]
                for typeplate in typeplate_container["typeplate"]["items"]
            ]
        )
        response = authenticated_client.get(f"/api/v1/typeplate/{int(typeplate_id)}")

        typeplate_container["typeplate_with_document"] = response.json()

        assert response.status_code == 200


@pytest.mark.order(122)
def test_get_typeplate_by_fake_id(
    authenticated_client: TestClient, typeplate_container, fake: Faker
):
    typeplate_id = fake.random_int(max=8000000, min=4000)
    response = authenticated_client.get(f"/api/v1/typeplate/{typeplate_id}")

    assert response.status_code == 404


@pytest.mark.order(123)
def test_typeplate_image_list(authenticated_client: TestClient, typeplate_images):
    response = authenticated_client.get("/api/v1/typeplate/images")
    typeplate_images["typeplate_images"] = response.json()

    assert response.status_code == 200


@pytest.mark.order(124)
def test_update_typeplate_api_without_eu_file(
    authenticated_client: TestClient,
    typeplate_container,
    typeplate_details,
    typeplate_images,
    fake: Faker,
):
    if len(typeplate_container["typeplate"]["items"]) <= 0:
        assert True
        return
    typeplate_id = random.choice(
        [
            typeplate["typeplateDetails"]["id"]
            for typeplate in typeplate_container["typeplate"]["items"]
        ]
    )
    typeplate_details["testResults"] = fake.text(max_nb_chars=200, ext_word_list=None)
    typeplate_details["euId"] = f"{fake.random_int()}{fake.word()}"
    typeplate_details["carbonFootprintLabel"] = fake.text(max_nb_chars=200, ext_word_list=None)

    choice = random.choice(typeplate_images["typeplate_images"])
    typeplate_image = [{"id": choice.get("id"), "name": choice.get("name")}]

    form_data = {
        "typeplate_data": json.dumps(typeplate_details),
        "typeplate_images": json.dumps(typeplate_image),
    }

    response = authenticated_client.put(
        f"/api/v1/typeplate/{int(typeplate_id)}",
        data=form_data,
    )

    assert response.status_code == 200


@pytest.mark.order(125)
def test_update_typeplate_with_eu_file(
    authenticated_client: TestClient,
    typeplate_container,
    typeplate_details,
    typeplate_images,
    fake: Faker,
):
    if len(typeplate_container["typeplate"]["items"]) <= 0:
        assert True
        return

    typeplate_id = random.choice(
        [
            typeplate["typeplateDetails"]["id"]
            for typeplate in typeplate_container["typeplate"]["items"]
        ]
    )

    fake_file = fake.file_name()
    document_content = fake.text().encode("utf-8")

    typeplate_details["testResults"] = fake.text(max_nb_chars=200, ext_word_list=None)
    typeplate_details["euId"] = f"{fake.random_int()}{fake.word()}"
    typeplate_details["carbonFootprintLabel"] = fake.text(max_nb_chars=200, ext_word_list=None)

    choice = random.choice(typeplate_images["typeplate_images"])
    typeplate_image = [{"id": choice.get("id"), "name": choice.get("name")}]

    form_data = {
        "typeplate_data": json.dumps(typeplate_details),
        "typeplate_images": json.dumps(typeplate_image),
    }

    response = authenticated_client.put(
        f"/api/v1/typeplate/{int(typeplate_id)}",
        data=form_data,
        files=[("eu_file", (fake_file, document_content, "application/pdf"))],
    )

    assert response.status_code == 200


@pytest.mark.order(126)
def test_update_typeplate_with_unauthenticated_client(
    client: TestClient,
    typeplate_container,
    typeplate_details,
    typeplate_images,
    fake: Faker,
):
    if len(typeplate_container["typeplate"]["items"]) <= 0:
        assert True
        return

    typeplate_id = random.choice(
        [
            typeplate["typeplateDetails"]["id"]
            for typeplate in typeplate_container["typeplate"]["items"]
        ]
    )

    fake_file = fake.file_name()
    document_content = fake.text().encode("utf-8")

    typeplate_details["testResults"] = fake.text(max_nb_chars=200, ext_word_list=None)
    typeplate_details["euId"] = f"{fake.random_int()}{fake.word()}"
    typeplate_details["carbonFootprintLabel"] = fake.text(max_nb_chars=200, ext_word_list=None)

    choice = random.choice(typeplate_images["typeplate_images"])
    typeplate_image = [{"id": choice.get("id"), "name": choice.get("name")}]

    form_data = {
        "typeplate_data": json.dumps(typeplate_details),
        "typeplate_images": json.dumps(typeplate_image),
    }

    response = client.put(
        f"/api/v1/typeplate/{int(typeplate_id)}",
        data=form_data,
        files=[("eu_file", (fake_file, document_content, "application/pdf"))],
    )

    assert response.status_code == 401


@pytest.mark.order(126)
def test_update_typeplate_with_fake_typeplate_id(
    authenticated_client: TestClient,
    typeplate_container,
    typeplate_details,
    typeplate_images,
    fake: Faker,
):
    typeplate_id = fake.random_int(max=8000000, min=4000)

    typeplate_details["testResults"] = fake.text(max_nb_chars=200, ext_word_list=None)
    typeplate_details["euId"] = f"{fake.random_int()}{fake.word()}"
    typeplate_details["carbonFootprintLabel"] = fake.text(max_nb_chars=200, ext_word_list=None)

    choice = random.choice(typeplate_images["typeplate_images"])
    typeplate_image = [{"id": choice.get("id"), "name": choice.get("name")}]

    form_data = {
        "typeplate_data": json.dumps(typeplate_details),
        "typeplate_images": json.dumps(typeplate_image),
    }

    response = authenticated_client.put(
        f"/api/v1/typeplate/{int(typeplate_id)}",
        data=form_data,
    )

    assert response.status_code == 404


@pytest.mark.order(127)
def test_get_typeplate_document(
    authenticated_client: TestClient,
    typeplate_container,
):
    if not typeplate_container or not typeplate_container["typeplate_with_document"]["euFile"]:
        assert True
        return

    typeplate = typeplate_container["typeplate_with_document"]

    typeplate_id = typeplate["id"]
    eu_file_id = typeplate["euFile"]["id"]

    response = authenticated_client.get(
        f"/api/v1/typeplate/docuemnt/{int(typeplate_id)}/{eu_file_id}",
    )

    assert response.status_code == 200


def test_get_typeplate_document_with_unauthenticated_client(
    client: TestClient,
    typeplate_container,
):
    if not typeplate_container or not typeplate_container["typeplate_with_document"]["euFile"]:
        assert True
        return

    typeplate = typeplate_container["typeplate_with_document"]

    typeplate_id = typeplate["id"]
    eu_file_id = typeplate["euFile"]["id"]

    response = client.get(
        f"/api/v1/typeplate/docuemnt/{int(typeplate_id)}/{eu_file_id}",
    )

    assert response.status_code == 401


def test_get_typeplate_document_with_fake_typeplate_id(
    authenticated_client: TestClient,
    typeplate_container,
):
    if not typeplate_container or not typeplate_container["typeplate_with_document"]["euFile"]:
        assert True
        return

    typeplate = typeplate_container["typeplate_with_document"]

    typeplate_id = typeplate["id"]
    eu_file_id = typeplate["euFile"]["id"]

    response = authenticated_client.get(
        f"/api/v1/typeplate/docuemnt/{int(typeplate_id) + 1000}/{eu_file_id}",
    )

    assert response.status_code == 404


@pytest.mark.order(128)
def test_delete_typeplate_document(
    authenticated_client: TestClient,
    typeplate_container,
):
    if not typeplate_container or not typeplate_container["typeplate_with_document"]["euFile"]:
        assert True
        return

    typeplate = typeplate_container["typeplate_with_document"]

    typeplate_id = typeplate["id"]
    eu_file_id = typeplate["euFile"]["id"]

    response = authenticated_client.delete(
        f"/api/v1/typeplate/document/{typeplate_id}/{eu_file_id}",
    )

    assert response.status_code == 204


def test_delete_typeplate_document_with_unauthenticated_client(
    client: TestClient,
    typeplate_container,
):
    if not typeplate_container or not typeplate_container["typeplate_with_document"]["euFile"]:
        assert True
        return

    typeplate = typeplate_container["typeplate_with_document"]

    typeplate_id = typeplate["id"]
    eu_file_id = typeplate["euFile"]["id"]

    response = client.delete(
        f"/api/v1/typeplate/document/{typeplate_id}/{eu_file_id}",
    )

    assert response.status_code == 401


def test_delete_typeplate_document_with_fake_typeplate_id(
    authenticated_client: TestClient,
    typeplate_container,
):
    if not typeplate_container or not typeplate_container["typeplate_with_document"]["euFile"]:
        assert True
        return

    typeplate = typeplate_container["typeplate_with_document"]

    typeplate_id = typeplate["id"]
    eu_file_id = typeplate["euFile"]["id"]

    response = authenticated_client.delete(
        f"/api/v1/typeplate/document/{typeplate_id + 1000}/{eu_file_id}",
    )

    assert response.status_code == 404
