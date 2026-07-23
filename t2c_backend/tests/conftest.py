import random
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

import alembic.config
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from main import app
from tests.utils.misc import Pagination
from utils.enums import (
    AssetStatus,
    AuditTaskStatus,
    InputType,
    ServiceTypes,
    TaskType,
)
from utils.misc import aware_utcnow


@pytest.fixture(scope="session")
def fake() -> Faker:
    return Faker(locale="fr_FR")


@pytest.fixture(scope="session")
def user_data_factory(fake: Faker):
    def _create_user() -> dict[str, dict[str, str]]:
        return {
            "credentials": {
                "email": fake.email(),
                "password": fake.password(
                    length=12,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                ),
            },
            "basics": {
                "firstName": fake.first_name(),
                "lastName": fake.last_name(),
            },
        }

    return _create_user


@pytest.fixture(scope="session")
def user_data(user_data_factory) -> dict[str, dict[str, str]]:
    return user_data_factory()


@pytest.fixture(scope="session")
def second_user_data(user_data_factory):
    return user_data_factory()


@pytest.fixture(scope="function")
def location(fake: Faker) -> dict[str, str]:
    return {
        "name": fake.name(),
        "street": fake.street_name(),
        "postcode": fake.postcode(),
        "city": fake.city(),
        "country": fake.country(),
        "region": fake.region(),
        "telNumber": fake.phone_number(),
        "mobileNumber": fake.phone_number(),
        "faxNumber": fake.phone_number(),
        "email": fake.email(),
    }


@pytest.fixture(scope="function")
def organization(fake: Faker) -> dict[str, str]:
    return {
        "name": fake.company(),
        "number": fake.phone_number(),
        "email": fake.company_email(),
    }


@pytest.fixture(scope="session")
def organization_container():
    return {}


@pytest.fixture(scope="session")
def database_migration() -> None:
    alembic_args = [
        "--raiseerr",
        "upgrade",
        "head",
    ]
    alembic.config.main(argv=alembic_args)


@pytest.fixture(scope="session")
def client(database_migration) -> Generator:
    """Return the test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def authenticated_client(database_migration, user_data) -> Generator:
    """Return the authenticated test client."""
    with TestClient(app) as c:
        r = c.post("/api/v1/login", json=user_data["credentials"])
        c.headers.update({"Authorization": f"Bearer {r.json()['access_token']}"})
        yield c


@pytest.fixture(scope="session")
def asset_type_category_group_container():
    return {}


@pytest.fixture(scope="session")
def asset_type_category_mapping_container():
    return {}


@pytest.fixture(scope="session")
def taxonomy_container():
    return {}


@pytest.fixture(scope="session")
def asset_type_category_field_options(fake: Faker) -> list[dict[str, str]]:
    return [
        {"optionLabel": fake.name(), "optionId": f"{fake.random_int()}"},
        {"optionLabel": fake.name(), "optionId": f"{fake.random_int()}"},
    ]


@pytest.fixture(scope="function")
def asset_type_category_field(fake: Faker) -> dict[str, str | bool | int | InputType | list[Any]]:
    return {
        "fieldName": fake.name(),
        "fieldPlaceHolder": fake.name(),
        "fieldDisplayName": fake.name(),
        "fieldIsRequired": fake.boolean(),
        "fieldOrder": fake.random_number(),
        "fieldType": InputType.text,
        "fieldGroupId": fake.random_int(min=1, max=9),
        "options": [],
    }


@pytest.fixture(scope="function")
def asset_type_category_fields(fake: Faker) -> list[dict]:
    return [
        {
            "fieldName": fake.name(),
            "fieldPlaceHolder": fake.name(),
            "fieldDisplayName": fake.name(),
            "fieldIsRequired": fake.boolean(),
            "fieldOrder": fake.random_number(),
            "fieldType": InputType.text,
            "fieldGroupId": fake.random_int(min=1, max=9),
            "options": [],
        },
        {
            "fieldName": fake.name(),
            "fieldPlaceHolder": fake.name(),
            "fieldDisplayName": fake.name(),
            "fieldIsRequired": fake.boolean(),
            "fieldOrder": fake.random_number(),
            "fieldType": InputType.text,
            "fieldGroupId": fake.random_int(min=1, max=9),
            "options": [],
        },
    ]


@pytest.fixture(scope="function")
def asset_type_category(fake: Faker) -> dict[str, str]:
    return {"name": fake.name(), "hasTypeplates": fake.boolean()}


@pytest.fixture(scope="session")
def asset_type_category_detail_container(fake: Faker) -> dict[str, str]:
    return {}


@pytest.fixture(scope="session")
def asset_type_field_options(fake: Faker) -> list[dict[str, str]]:
    return [
        {"optionId": f"{fake.random_int()}"},
    ]


@pytest.fixture(scope="session")
def asset_type_field(fake: Faker) -> dict[str, str | list[Any] | InputType]:
    return {
        "fieldId": fake.random_int(),
        "responseValue": fake.name(),
        "assetTypeFieldOptions": [],
    }


@pytest.fixture(scope="session")
def asset_type(fake: Faker) -> dict[str, str]:
    return {
        "name": fake.name(),
        "videoTitle": fake.name(),
        "videoLinks": fake.name(),
        "webLink": fake.name(),
        "webLinkTitle": fake.name(),
        "description": fake.name(),
        "weight": fake.random_int(),
        "manufacturer": fake.name(),
    }


@pytest.fixture(scope="function")
def updated_asset_type(fake: Faker) -> dict[str, str]:
    return {
        "name": fake.name(),
        "videoTitle": fake.name(),
        "videoLinks": fake.name(),
        "webLink": fake.name(),
        "webLinkTitle": fake.name(),
        "description": fake.name(),
        "weight": fake.random_int(),
        "manufacturer": fake.name(),
    }


@pytest.fixture(scope="session")
def asset(fake: Faker) -> dict[str, int]:
    return {
        "location": fake.random_number(fix_len=True),
        "assetId": f"{fake.random_number(fix_len=True)}",
        "manufacturingDate": int((fake.date_time()).timestamp()),
        "status": fake.name(),
        "serialNo": f"{fake.random_number(fix_len=True)}",
        "economicOperator": fake.name(),
        "assetType": fake.random_number(fix_len=True),
        "services": [],
        "deviceId": fake.uuid4(),
    }


@pytest.fixture(scope="function")
def update_asset(fake: Faker) -> dict:
    return {
        "location": fake.random_number(fix_len=True),
        "assetId": f"{fake.random_number(fix_len=True)}",
        "manufacturingDate": int((fake.date_time()).timestamp()),
        "status": random.choice(list(AssetStatus)),
        "serialNo": f"{fake.random_number(fix_len=True)}",
        "economicOperator": fake.name(),
        "assetType": fake.random_number(fix_len=True),
    }


@pytest.fixture(scope="session")
def typeplate_details(fake: Faker) -> dict[str, str]:
    return {
        "testResults": fake.name(),
        "euId": fake.name(),
        "carbonFootprintLabel": fake.name(),
    }


@pytest.fixture(scope="session")
def typeplate_container() -> dict[str, str]:
    return {}


@pytest.fixture(scope="session")
def typeplate_images() -> dict[str, str]:
    return {}


@pytest.fixture(scope="session")
def container():
    return {}


@pytest.fixture(scope="session")
def asset_type_container():
    return {}


@pytest.fixture(scope="session")
def asset_container():
    return {}


@pytest.fixture(scope="function")
def asset_service(fake: Faker):
    service_date = int((fake.date_time()).timestamp()) + int(aware_utcnow().timestamp())
    return {
        "serviceName": fake.name(),
        "serviceProviderName": fake.name(),
        "contact": fake.phone_number(),
        "expireDate": service_date + 3600 * 24,
        "serviceDate": service_date,
        "serviceType": ServiceTypes.basic,
        "web": fake.url(),
        "email": fake.email(),
    }


@pytest.fixture(scope="session")
def service_container():
    return []


@pytest.fixture(scope="session")
def display_asset_container():
    return {}


@pytest.fixture(scope="session")
def asset_usage_session_container():
    return {}


@pytest.fixture(scope="function")
def audit_task(fake: Faker) -> dict[str, str | AuditTaskStatus]:
    return {
        "taskName": fake.word(),
        "taskType": random.choice(list(TaskType)),
        "status": random.choice(list(AuditTaskStatus)),
        "performedByOrg": fake.word(),
        "roleOfOrg": fake.word(),
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
    }


@pytest.fixture(scope="session")
def audit_task_container():
    return []


@pytest.fixture(scope="session")
def audit(fake: Faker) -> dict[str, int | list[Any]]:
    now = datetime.now(UTC)
    return {
        "inspectionDate": int(now.timestamp()),
        "validUntil": int((now + timedelta(days=random.randint(1, 60))).timestamp()),
        "auditTasks": [],
    }


@pytest.fixture(scope="session")
def audit_container():
    return []


@pytest.fixture(scope="session")
def asset_type_with_documents_container():
    return {}


@pytest.fixture(scope="session")
def create_pagination(fake: Faker):
    page_size = fake.random_int(1, 10)
    page = fake.random_int(1, 1)

    return Pagination(pagesize=page_size, page=page)


@pytest.fixture(scope="function")
def invalid_id(fake: Faker):
    return fake.random_int(min=10_00_001, max=20_00_000)


@pytest.fixture(scope="function")
def word_to_search(fake: Faker):
    return fake.domain_name()


@pytest.fixture(scope="function")
def organization_role(fake: Faker):
    return {
        "name": fake.first_name(),
        "permissions": [
            fake.last_name(),
        ],
    }
