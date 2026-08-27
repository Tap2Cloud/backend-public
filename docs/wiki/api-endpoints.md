# API Endpoints

## Module Overview

The `endpoints` package exposes the REST API under `/api/v1`. Every domain has a router of fully-spelled-out routes; OpenAPI tags and the `/v1` prefix are applied centrally when sub-routers are included. Routes obtain their dependencies (services, DB session, current token) through FastAPI dependency injection, and list endpoints return the paginated `CustomPage[...]` wrapper.

## Architecture Diagram

```mermaid
graph TD
  Main[CustomFastAPI] --> ApiRouter[api_router /api]
  ApiRouter --> V1[v1 router /v1]
  V1 --> Auth[authentication/register/token]
  V1 --> AssetR[asset / asset-type / category]
  V1 --> PassR[asset-pass]
  V1 --> AuditR[audit / service / typeplate]
  V1 --> OrgR[organization / user / location / role]
  V1 --> Misc[dashboard / product pass type / health / instruction-manual]
  Auth --> Sec[JWT bearers]
  AssetR --> Svc[get_services → DictContainer]
  PassR --> Svc
```

## Router Wiring

`endpoints/router.py` builds `api_router` and includes the `v1` rest router; `CustomFastAPI` mounts it under `API_STR` (`/api`). The parent router lives in **`endpoints/v1/rest/__init__.py`** — an `APIRouter(prefix="/v1")` that includes each sub-router with a central `tags=[...]`. (`endpoints/v1/__init__.py` itself is empty.) Each sub-router file declares a bare `router = APIRouter()` with full paths on each decorator.

`operation_id` is set on most but not all routes — 52 of 66 today. The uncovered ones are every route in `audit.py`, plus `POST /login`, `POST /register`, `GET /health`, `GET /token/refresh`, `GET /product-pass-type`, `GET /instruction-manual` and `GET /filter/location`; those fall back to FastAPI's generated ids, which makes their client-SDK method names less stable across refactors.

## Endpoint Groups

### Authentication (public)

- **`POST /login`** — verifies credentials via `user_service.login`, mints `AccessToken` + `RefreshToken` from `app.clients.token_backend`, returns `UserLoginResponse`.
- **`POST /register`** — `user_service.register_user`, issues an email-verification token via `user_email_token_service`, and auto-logs-in the new user with a token pair (`TokenResponse`).
- **`GET /token/refresh`** — guarded by `JWTAPIRefreshTokenBearer`; returns a fresh access token (`RefreshTokenResponse`). There is no logout endpoint (stateless JWT).

### Assets & passports

- `asset` — create/update/delete, `PUT /asset` (filtered paginated list via `SelectiveFilters` body), `GET /asset/{id}`.
- `asset-pass` — the digital product passport surface, in its own router (`asset_pass.py`, tag `asset-pass`). See below.
- `asset-type` — CRUD, filtered list, and document sub-routes (custom-field docs, instruction-manual downloads via streaming); create/update are multipart.
- `asset-type-category` — CRUD, category groups, and filter/mapping endpoints backing dropdowns.

#### The `asset-pass` router

`endpoints/v1/rest/asset_pass.py` holds the three passport routes. `GET /asset-pass` is the only guarded one:

| Route | Auth | Purpose |
| --- | --- | --- |
| `GET /asset-pass` | `list_asset_pass` flag | Paginated `DetailedAssetPassResponse` list, scoped to `token.organization_id`. |
| `GET /asset-pass/{passId}` | **public** | The passport view for a single asset, resolved by `pass_id`. |
| `GET /asset-pass/{passId}/document/{documentFor}/{documentId}` | **public** | Streams one document attached to that passport. |

The document route is the passport's read-only file surface — it lets a passport page load its own PDFs and images without a token, given only the (unguessable) `pass_id`:

```python
@router.get(
    "/asset-pass/{passId}/document/{documentFor}/{documentId}", response_class=StreamingResponse
)
async def get_asset_pass_document(
    pass_id: str = Path(..., alias="passId"),
    document_for: DocumentFor = Path(..., alias="documentFor"),
    document_id: str = Path(..., alias="documentId"),
    download: bool = Query(False),
    services: DictContainer = Depends(get_services),
):
    return await services.asset_service.get_asset_pass_document(
        pass_id=pass_id,
        document_for=document_for,
        document_id=document_id,
        as_attachment=download,
    )
```

- `documentFor` is the `DocumentFor` enum, so an unknown value is rejected by FastAPI as **422** before the service runs; a well-formed but unmatched document is **404**.
- `download=true` switches `Content-Disposition` from `inline` to `attachment`; the filename is always the stored document name.
- The declared OpenAPI response content type is `application/octet-stream`, but the handler serves the document's real content type when one is known — octet-stream is only the fallback.
- Reachability is bounded by the passport: the service resolves the asset from `passId` first and then searches **only that asset's** own documents, so a `documentId` belonging to another asset returns 404. See [Services](services.md) for the resolution rules.

### Operations

- `audit` — create tasks/audits (multipart with document uploads), list (date-range filters), deletes, task-document download, and a localized PDF `audit-report`.
- `service` — CRUD and paginated list of asset service/maintenance records.
- `typeplate` — list images, list/get/update typeplates (multipart EU file), delete document, and EU-file streaming download.
- `instruction-manual` — list/upload/delete instruction-manual documents (backed by `asset_type_service`).

### Organization & users

- `organization` — create org + first location (multipart), update, delete, get details, and org role list/create (which raise `UnAuthorizedError` when the token has no org). Role creation takes `RoleCreate` (`name` + `permissions: list[str]`), though only the name is persisted today — see [Permissions Reference](permissions-reference.md).
- `user` — profile get/update (multipart avatar), org-user paginated listing (`OrganizationUsersCustomPage`), password change, and two deletes: `DELETE /user/{cascadeOrg}` (self) and `DELETE /organization/user/{userId}/{cascadeOrg}` (another member). The `cascadeOrg` path flag decides what happens when the target is the org's **last** user: `true` deletes the whole organization, `false` returns `400 Unable to delete this user`. Because that escalates to org deletion, both routes require `organization_delete` in addition to their own flag when `cascadeOrg` is set.
- `location` — update current location, list org locations.
- `product_pass_type` — list product pass types.

### Misc

- `dashboard` — `GET /dashboard/summary` returns aggregate counts (`DashboardResponse`).
- `health` — `GET /health` returns version + status; no auth, no service.

## Auth & Dependency Injection

```mermaid
sequenceDiagram
  participant C as Client
  participant Route
  participant Bearer as JWTAPIAccessTokenBearer
  participant GS as get_services
  C->>Route: request + Bearer token
  Route->>Bearer: verify + re-hydrate org/location/roles from DB
  Bearer->>Bearer: check required permission flag
  Bearer-->>Route: AccessToken (or 403)
  Route->>GS: Depends(get_services)
  GS->>GS: wire each service with request-scoped session
  GS-->>Route: app.services (DictContainer)
  Route->>Route: services.<name>_service.<method>(...)
```

- **Authentication + authorization** — `token: AccessToken = Depends(JWTAPIAccessTokenBearer(permissions={"asset_delete": True}))`. Almost every protected route declares the permission flag it requires **on the bearer itself**; the bearer re-hydrates the token's org/location/roles from the DB on each request and rejects the call with **403 `Insufficient permissions.`** when the caller's roles don't grant the flag. The full route→flag matrix lives in [Permissions Reference](permissions-reference.md).
- **Row scoping is separate** — the flag says *what kind of* operation is allowed; **which rows** are reachable is enforced inside the services from `token.location_id` / `token.organization_id` (raising `NotFoundError` on a mismatch, or `UnAuthorizedError` in the org role routes when the token has no org).
- **Compound operations** — a few handlers add a second check when a request parameter widens the blast radius: both user-delete routes additionally require `organization_delete` when `cascadeOrg` is true, via `JWTAPIAccessTokenBearer.user_permissions(token)`.
- **Services** — `services: DictContainer = Depends(get_services)`, where `get_services` nests `Depends(get_db_session)` and wires every registered service onto the request-scoped session, accessed as `services.<name>_service`.
- **Public routes** — `/login`, `/register`, `/health`, `/asset-pass/{passId}`, and `/asset-pass/{passId}/document/{documentFor}/{documentId}`. The two passport routes are unauthenticated by design: the `pass_id` is the capability, so anyone holding it can read that passport and stream its documents.
- **Authenticated but unguarded routes** — `POST /organization` (bootstrap: the caller has just registered and holds no org roles yet), `GET /user/profile` (own profile), `GET /product-pass-type` and `GET /asset-type-category-group` (static reference data), and `GET /dashboard/summary`. `GET /token/refresh` requires a valid refresh token but declares no permission — the refresh bearer skips the DB round-trip, so its token has no roles to check.
- **Conventions** — complex/filtered list endpoints use `PUT` with a body (`SelectiveFilters`) rather than `GET`; pagination params are `page`/`pageSize` (1–1000); file endpoints return `StreamingResponse`; multipart is used for create/update of asset types, typeplates, organizations, user profile, and audits.

> Minor notes carried from the source: the typeplate download path contains a typo (`/typeplate/docuemnt/...`), and `instruction_manual` routes reuse `asset_type_service`.

## Dependencies

```mermaid
graph LR
  Endpoints --> Services
  Endpoints --> Security
  Endpoints --> Schemas
  Endpoints --> CorePagination[Core: CustomPage]
```

## Cross-references

- [Services](services.md) — the business logic each route delegates to
- [Security & Permissions](security-and-permissions.md) — the JWT bearers and token flows
- [Permissions Reference](permissions-reference.md) — the complete route → permission flag matrix
- [Schemas](schemas.md) — request/response models
- [Core Infrastructure](core-infrastructure.md) — `get_db_session`, pagination
- [Application Bootstrap](application-bootstrap.md) — router mounting and `get_services`
