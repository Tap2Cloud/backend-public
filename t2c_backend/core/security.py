from fastapi import Request, WebSocket, WebSocketException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from t2c_backend.core.permissions import Permissions
from t2c_backend.schemas.v1.token import AccessToken, RefreshToken, Token
from t2c_backend.services import UserService
from t2c_backend.utils.enums import Role
from t2c_backend.utils.errors import TokenError, UnAuthenticatedError, UnAuthorizedError


class BaseJWTAPIBearer:
    roles: set[Role]
    permissions: dict[str, bool]

    def __init__(self, roles: set[Role], permissions: dict[str, bool]) -> None:
        self.roles = roles or set()
        self.permissions = permissions or {}

    async def verify_jwt(self, jwt_token: str, app) -> "Token":
        raise NotImplementedError("Subclasses must implement `verify_jwt`.")

    def check_role(self, token: "Token") -> bool:
        return all(
            str(role) in {user_role["name"] for user_role in token.roles} for role in self.roles
        )

    @staticmethod
    def user_permissions(token: "Token"):
        return {
            flag
            for role in token.roles
            for flag, check in dict(Permissions(int(role["permissions"]))).items()
            if check
        }

    def check_permission(self, token: "Token") -> bool:
        user_permissions = self.user_permissions(token)
        valid_checked_permissions = {
            permission
            for permission, check in self.permissions.items()
            if check and permission in Permissions.VALID_FLAGS
        }
        return set(valid_checked_permissions).issubset(user_permissions)


class JWTAPIBearer(BaseJWTAPIBearer, HTTPBearer):
    def __init__(
        self,
        roles: set["Role"] = None,
        permissions: dict[str, bool] = None,
        auto_error: bool = False,
    ) -> None:
        BaseJWTAPIBearer.__init__(self, roles=roles, permissions=permissions)
        HTTPBearer.__init__(self, auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request,
        )
        if credentials:
            if not credentials.scheme == "Bearer":
                raise UnAuthorizedError("Invalid authentication scheme.")
            try:
                token = await self.verify_jwt(credentials.credentials, app=request.app)

                # Check roles if specified
                if self.roles and not self.check_role(token):
                    raise UnAuthenticatedError("Insufficient roles.")

                # Check permissions if specified
                if self.permissions and not self.check_permission(token):
                    raise UnAuthenticatedError("Insufficient permissions.")

                return token
            except TokenError as e:
                raise UnAuthorizedError(str(e))
        else:
            raise UnAuthorizedError("Invalid authorization code.")


class JWTAPIAccessTokenBearer(JWTAPIBearer):
    async def verify_jwt(self, jwt_token: str, app):
        async with app.database_engine.async_session_factory_creator()() as session:
            access_token = AccessToken(app.clients.token_backend, jwt_token)
            access_token.update_payload(
                await UserService(app, session).get_user_org_location_and_roles(
                    access_token.user_id,
                ),
            )
            return access_token


class JWTAPIRefreshTokenBearer(JWTAPIBearer):
    async def verify_jwt(self, jwt_token: str, app):
        return RefreshToken(app.clients.token_backend, jwt_token)


class JWTWebSocketBearer(BaseJWTAPIBearer):
    def __init__(self, roles: set[Role] = None, permissions: dict[str, bool] = None) -> None:
        BaseJWTAPIBearer.__init__(self, roles=roles, permissions=permissions)

    async def __call__(self, websocket: WebSocket):
        token = websocket.query_params.get("token")
        if token:
            try:
                return await self.verify_jwt(token, websocket.app)
            except TokenError as e:
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))
        else:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid authorization code.",
            )


class JWTWebSocketAccessTokenBearer(JWTWebSocketBearer):
    async def verify_jwt(self, jwt_token: str, app):
        async with app.database_engine.async_session_factory_creator()() as session:
            access_token = AccessToken(app.clients.token_backend, jwt_token)
            access_token.update_payload(
                await UserService(app, session).get_user_org_location_and_roles(
                    access_token.user_id,
                ),
            )
            return access_token


class JWTWebSocketRefreshTokenBearer(JWTWebSocketBearer):
    async def verify_jwt(self, jwt_token: str, app):
        return RefreshToken(app.clients.token_backend, jwt_token)
