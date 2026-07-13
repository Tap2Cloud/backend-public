# Services

## Module Overview

The `services` package is the business-logic layer between routers and the data layer. Each domain service wraps one primary model in a `BaseRepository`, is constructed per-request with the request-scoped DB session, and is resolved through the session-based `DictContainer` (`app.services.<name>_service`). Services reach peers and external clients through the app (`self.app.services.*`, `self.app.clients.*`).

## Architecture Diagram

```mermaid
graph TD
  GS[get_services] --> Reg[__services__ registry]
  Reg --> Setup[setup app, session]
  Setup --> Add[app.add_service → DictContainer]
  Svc[XService] --> Repo[BaseRepository]
  Repo --> Session[request-scoped AsyncSession]
  Svc --> Peers[self.app.services.*]
  Svc --> Clients[self.app.clients.*]
```

## Conventions

Every domain service follows an identical shape:

```python
class XService:
    _model = SomeModel
    def __init__(self, app, session):
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
```

- **Registration** — each module exposes `setup(app, session, ...)` that calls `app.add_service(XService(app, session), session.info["session_id"])`. The registry key is `underscore(ClassName)` (e.g. `AssetService → asset_service`).
- **Resolution** — `services/__init__.py` builds the `__services__` list of `(class, setup)` pairs and exposes `get_services()`, which wires every service onto the request's session and returns `app.services`. There is **no shared base class** — the pattern is duck-typed convention.
- **Peer calls** — services reuse each other's `.repository` directly (e.g. `OrganizationService` uses `user_service.repository`, `role_service.repository`), sharing the same session-scoped instances.
- **Pagination** — list methods use `fastapi_pagination.ext.sqlalchemy.apaginate` with `CustomParams`/`CustomPage` and a `transformer` mapping ORM rows to `schemas.v1` responses.

## Component Descriptions

### Auth & identity

- **`Authentication`** — the only session-less service (no repository). `generate_encoded_password()` (random salt + PBKDF2-HMAC-SHA256, 100k iterations), `verify_hash()`, and frontend link builders for email verification / password reset (`FRONTEND_URL`).
- **`UserService`** (`User`) — `get_user_org_location_and_roles()` (**auth-critical**, feeds token re-hydration), `login`, `register_user`, `change_password`, `get_user_profile`, `update_user_profile`, deletes, and `organization_user_handler` (paginated/filterable org-user listing with status counts).
- **`UserEmailTokenService`** (`UserEmailToken`) — `create_token(user_id, TokenType)` issues one-time email/reset tokens.
- **`RoleService`** (`Role`) — list and create org roles.

### Tenancy

- **`OrganizationService`** (`Organization`) — `create_organization_with_location()` bootstraps an org, its default roles (`Role.organization_roles()`), and its first location (assigning the user `owner`); plus update/get (with computed counts)/delete.
- **`LocationService`** (`Location`) — create/update/list locations and user-location lookups.
- **`TaxonomyService`** (`Taxonomy`) — read-only taxonomy listing.

### Asset definition

- **`AssetTypeCategoryService`** (`AssetTypeCategory`) — manages the reusable category templates (dynamic form definitions with grouped fields and options); create/update/get/list with duplicate-order guards; maps `IntegrityError → AlreadyExistsError`.
- **`AssetTypeService`** (`AssetType`) — the most document-heavy service: builds asset types from a category template, manages custom fields, typeplates, EU files, instruction manuals, and per-field media through `app.clients.storage.save_document` keyed by `DocumentFor`. Provides streaming document downloads.
- **`TypeplateService`** (`Typeplate`) — manages product typeplates (EU declaration files, test results, image mappings); list/get/update/delete with storage-backed documents.

### Asset operations

- **`AssetService`** (`Asset`) — CRUD and listing; generates the passport `pass_id` via `app.clients.cryptography.encode(f"{location.id}_{device_id}")`; deep eager-loaded `list_asset_pass` / `get_asset_pass_by_pass_id` for public passport views.
- **`ServiceService`** (`Service`) — maintenance/service records; validates asset ownership by location and blocks editing expired services (`aware_utcnow()`).
- **`AuditService`** (`Audit`) — inspection audits, tasks, and documents; generates a **localized landscape-A4 PDF report** with ReportLab + Babel + i18n `_()`, with color-coded task statuses.

### Aggregation

- **`DashboardService`** — atypical (`_model = None`, uses `self.session` directly): `get_dashboard_statistics()` runs count queries for assets, asset types, typeplates, instruction manuals, services, and inspections, plus a "shop" count of same-taxonomy assets in other orgs.

## Dependencies

```mermaid
graph LR
  Services --> Repo[Core: BaseRepository]
  Services --> Models
  Services --> Schemas
  Services --> Clients[Clients: storage, cryptography]
  Endpoints --> Services
```

## Key APIs

```python
# Inside a route, services are resolved by name off the request-scoped container:
user = await services.user_service.login(email, password)
ctx  = await services.user_service.get_user_org_location_and_roles(user.id)

# Cross-service reuse shares the session-scoped repositories:
await self.app.services.role_service.repository.save_all(default_roles)
```

## Cross-references

- [Core Infrastructure](core-infrastructure.md) — `BaseRepository`, sessions, pagination
- [Data Models](data-models.md) — the entities services persist
- [Clients](clients.md) — storage and cryptography clients used by services
- [API Endpoints](api-endpoints.md) — the routes that call these services
- [Application Bootstrap](application-bootstrap.md) — service registration via `add_service`
