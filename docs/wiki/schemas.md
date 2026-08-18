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

- **Asset** — `CreateAsset`/`UpdateAsset`, `AssetResponse`, lightweight `DisplayAsset`, and the digital-passport views `AssetPassResponse` / `DetailedAssetPassResponse` (aggregating asset type, category, audits, product pass type). `SelectiveFilters` is the filter body for list endpoints.
- **Asset Type** — `CreateAssetTypeRequest`/`UpdateAssetTypeRequest` (multipart, `fields: conlist(BaseField, min_length=1)`), `AssetTypeResponse` (with `form`, instruction manuals, optional `TypeplateResponse`), plus nested `FormData`/`AssetTypeField`.
- **Asset Type Category** — `CreateAssetTypeCategoryRequest`/`UpdateAssetTypeCategoryRequest` with validators enforcing per-`InputType` option rules and rejecting duplicate field orders/names; `Field`/`FieldOption`, `AssetTypeCategoryResponse`, `DisplayAssetTypeCategory`. `AssetTypeCategoryResponse.user` is `DisplayUser | None`: the creator is now a nullable "created by" reference (`ON DELETE SET NULL`), so the response must tolerate a deleted creator — `user=DisplayUser.convert(category.user) if category.user else None`. See [Data Models](data-models.md).
- **Audit** — `CreateAuditTask`, `CreateAudit` (validates `inspection_date <= valid_until`), `AuditResponse`, `AssetAuditResponse`.
- **Service** — `CreateService` (validates `expireDate >= serviceDate`), `UpdateService`, `ServiceResponse`, `AssetServiceResponse`.
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
- **Mappers** — static `convert()`/`from_model()`/`from_list()`/`to_orm()` do explicit field-by-field ORM↔schema mapping (including datetime→epoch conversion).
- **Validators** — a recurring `@model_validator(mode="before")` `validate_to_json` accepts either a raw JSON string or an uploaded file body (multipart pattern); business-rule validators raise `BadRequestError`. `conlist(..., min_length=1)` enforces non-empty nested lists.
- **Pagination** — represented via the generic `CustomPage[T]` from [Core Infrastructure](core-infrastructure.md), parameterized per response type (or subclassed to add an `extra` payload).

## Dependencies

```mermaid
graph LR
  Schemas --> CorePagination[Core: CustomPage]
  Schemas --> Clients[Clients: token_backend]
  Schemas --> Utils[Utilities: enums, errors, datetime]
  Endpoints --> Schemas
```

## Cross-references

- [API Endpoints](api-endpoints.md) — where these DTOs are used as request/response models
- [Data Models](data-models.md) — the ORM entities these schemas map to
- [Security & Permissions](security-and-permissions.md) — the token classes
- [Permissions Reference](permissions-reference.md) — what the `permissions` integer in `RoleBase` means
- [Core Infrastructure](core-infrastructure.md) — `CustomPage` pagination
