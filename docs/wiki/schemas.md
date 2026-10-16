# Schemas

## Module Overview

The `schemas/v1` package holds the Pydantic request/response DTOs for the API. Nearly every schema enables `from_attributes=True` and provides explicit `convert` / `from_model` / `from_list` / `to_orm` mapper methods to translate between ORM objects and wire representations. The most distinctive members are the JWT token classes in `token.py` (used by auth) and a family of multipart-form validators.

## Architecture Diagram

```mermaid
graph TD
  Endpoints --> Schemas
  Schemas --> Token[token.py<br/>Token/AccessToken/RefreshToken]
  Schemas --> Image[image.Image<br/>base64 data URI]
  Schemas --> Domain[Domain DTOs<br/>asset/asset_type/...]
  Domain --> Convert[convert / from_model / to_orm]
  Domain --> Validators[validate_to_json<br/>business-rule validators]
  Schemas --> Pagination[CustomPage from core.pagination]
```

## Component Descriptions

### `token.py` — auth tokens

The only non-declarative module. `Token` wraps a JWT payload dict: it decodes an incoming token via the `token_backend` (wrapping failures as `TokenError`) or seeds a fresh payload with `exp`/`iat`/`jti`; `str(token)` signs and returns the encoded JWT. Claim keys are module constants (`user_id`, `organization_id`, `location_id`, `roles`, `jti`, `token_type`). `AccessToken` (1 day) and `RefreshToken` (7 days) set `token_type`/`lifetime`. Response models: `TokenResponse` (access+refresh) and `RefreshTokenResponse` (access only). See [Security & Permissions](security-and-permissions.md).

The `roles` claim is what authorization reads: `update_payload()` injects a list of
`{"id", "name", "permissions"}` dicts freshly queried per request, and the bearer decodes each
`permissions` integer into flags. The claim is **not** present in the signed JWT the client holds — it is
added server-side after decoding, so permissions can never be forged or go stale.

### Domain DTOs

Each domain has request and response schemas. Highlights:

- **Asset** — `CreateAsset`/`UpdateAsset` (`status` is typed as the `AssetStatus` enum, so unknown values are rejected at validation; `CreateAsset.manufacturingDate` is `EpochSeconds` and an `after` validator rejects values `<= 0`), `AssetResponse`, lightweight `DisplayAsset`, and the digital-passport views `AssetPassResponse` / `DetailedAssetPassResponse` (aggregating asset type, category, audits, product pass type). `SelectiveFilters` is the filter body for list endpoints.
- **Asset Type** — `CreateAssetTypeRequest`/`UpdateAssetTypeRequest` (multipart, `fields: conlist(BaseField, min_length=1)`), `AssetTypeResponse` (with `form`, instruction manuals, optional `TypeplateResponse`), plus nested `FormData`/`AssetTypeField`.
- **Asset Type Category** — `CreateAssetTypeCategoryRequest`/`UpdateAssetTypeCategoryRequest` with `before` validators that enforce:
  - **Option rules per field type** — `radio`, `checkbox`, `multiselect` and `select` need more than one option, with unique `optionId`s; every other type must have no options.
  - **Field-list rules** — no duplicate `fieldOrder` or `fieldName`, `fieldOrder > 0`, and **at least one field with `fieldIsRequired: true`**. The update request also rejects duplicate field `id`s (and duplicate option `id`s).

  The update DTOs (`UpdateBaseFields`, `UpdateBaseFieldOption`) describe the **complete desired field list**: `id` is nullable (`None` = new field/option, otherwise the existing row to keep/update), and `fieldName`, `fieldDisplayName`, `fieldOrder`, `fieldGroupId`, `fieldType`, `fieldIsRequired`, `optionId` and `optionLabel` are all required. `fieldPlaceHolder` is optional (defaults to `None`) on both request `BaseField` and response `Field`. Also `Field`/`FieldOption`, `AssetTypeCategoryResponse`, `DisplayAssetTypeCategory`. `AssetTypeCategoryResponse.user` is `DisplayUser | None`: the creator is now a nullable "created by" reference (`ON DELETE SET NULL`), so the response must tolerate a deleted creator — `user=DisplayUser.convert(category.user) if category.user else None`. See [Data Models](data-models.md).
- **Audit** — `CreateAuditTask`, `CreateAudit` (validates `inspection_date <= valid_until`; both are `EpochSeconds`), `AuditResponse`, `AssetAuditResponse`. `AuditTaskResponse.taskType`/`status` are typed as the `TaskType`/`AuditTaskStatus` enums. `validUntil` is now emitted straight from the timezone-aware column via `datetime_to_epoch` (no more `date` → midnight combination).
- **Service** — `CreateService` (`EpochSeconds` dates; an `after` validator raises `BadRequestError` unless `expireDate >= serviceDate`), `UpdateService`, `ServiceResponse`, `AssetServiceResponse`.
- **Organization / Location / ProductPassType** — layered inheritance; `DisplayOrganization` is the common base with two branches off it: `Organization` (adds `productPassType`) and `DetailedOrganization → OrganizationDetails` (adds `locationCount`/`userCount`/`roleCount`). `LocationCreateRequest → LocationBaseResponse → Location`; `ProductPassType` is dual-use. `LocationBaseResponse.organization` is typed as `Organization` (not `DisplayOrganization`), so location responses carry the nested `productPassType` — which means the service must eager-load `Organization.product_pass_type`.
- **User** — `UserLogin`/`UserLoginResponse` (reuses `TokenResponse`), `UserRegisterRequest`, `ChangePasswordRequest`, `DisplayUser`/`UserResponse`/`OrganizationUser`, and `OrganizationUsersCustomPage` (a `CustomPage` subclass adding `extra: UserCount`).
- **Dashboard / Documents / Health** — `DashboardResponse` is a flat counter DTO (`assetType`, `typeplate`, `asset`, `service`, `instructionManual`, `inspection`, plus `timeRecording`/`iot` hard-coded to `0`); the former `shop` counter has been dropped. Also `DocumentResponse` and `Health` (the only schema without `from_attributes`).
- **Role** (`role.py`) — the authorization DTOs, and the one place the permission bitmask crosses the wire:
  - `RoleBase` — the response (`id`, `name`, `permissions: int`), with `convert`/`convert_` mappers. `permissions` is emitted as the **raw integer bitmask**; clients decode the bits themselves.
  - `RoleCreate` — the request (`name`, `permissions: list[str]`), i.e. flag *names* in, integer out. Be aware the list is currently **not persisted** by `RoleService`, and the names are not validated against `Permissions.VALID_FLAGS`. See [Permissions Reference](permissions-reference.md).

### `image.Image`

A shared serialization helper (not a request/response DTO): async `from_file(UploadFile)` base64-encodes an upload; `get_string()` returns a `data:` URI. Reused for organization logos, user avatars, and typeplate images.

## Conventions

- **Naming** — requests are `Create*`/`Update*` (update variants usually all-optional); responses are `*Response` (full) and `Display*` (lightweight nested summaries).
- **Config** — `ConfigDict(from_attributes=True)` almost everywhere; `populate_by_name=True` on multipart schemas.
- **Aliasing** — snake_case Python attributes exposed as camelCase JSON via `Field(alias=...)`. Where a domain `Field` model exists, Pydantic's `Field` is imported as `PydanticField`.
- **Mappers** — static `convert()`/`from_model()`/`from_list()`/`to_orm()` do explicit field-by-field ORM↔schema mapping.
- **Timestamps** — all datetimes travel as integer epoch seconds. Outgoing values go through `datetime_to_epoch(dt)` (`calendar.timegm(dt.utctimetuple())`) and incoming ones through `datetime_from_epoch(ts)` (a UTC-aware `datetime`), both in `utils.misc`; the old `int(dt.timestamp())` / naive `datetime.fromtimestamp()` calls are gone. Epoch inputs are typed `EpochSeconds` — an `int` bounded to `MIN_EPOCH_SECONDS`/`MAX_EPOCH_SECONDS` (1900-01-01 through 9998-12-31 UTC), so out-of-range values fail validation instead of overflowing on conversion.
- **Validators** — a recurring `@model_validator(mode="before")` `validate_to_json` accepts either a raw JSON string or an uploaded file body (multipart pattern); business-rule validators raise `BadRequestError`. `conlist(..., min_length=1)` enforces non-empty nested lists.
- **Pagination** — represented via the generic `CustomPage[T]` from [Core Infrastructure](core-infrastructure.md), parameterized per response type (or subclassed to add an `extra` payload).

## Dependencies

```mermaid
graph LR
  Schemas --> CorePagination[Core: CustomPage]
  Schemas --> Clients[Clients: token_backend]
  Schemas --> Utils[Utilities: enums, errors, epoch helpers]
  Endpoints --> Schemas
```

## Cross-references

- [API Endpoints](api-endpoints.md) — where these DTOs are used as request/response models
- [Data Models](data-models.md) — the ORM entities these schemas map to
- [Security & Permissions](security-and-permissions.md) — the token classes
- [Permissions Reference](permissions-reference.md) — what the `permissions` integer in `RoleBase` means
- [Core Infrastructure](core-infrastructure.md) — `CustomPage` pagination
