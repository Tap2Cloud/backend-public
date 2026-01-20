import decimal
import json
from datetime import timedelta

import jwt
from jwt import InvalidAlgorithmError, InvalidTokenError, PyJWKClient, PyJWKClientError, algorithms

from t2c_backend.clients.token_backend.config import Config
from t2c_backend.utils.errors import TokenBackendError


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if float(o) == int(o):
                return int(o)
            else:
                return float(o)
        return super().default(o)


class TokenBackend:
    ALLOWED_ALGORITHMS = {
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
        "ES256",
        "ES384",
        "ES512",
    }

    def __init__(
        self,
        app,
        algorithm,
        signing_key=None,
        verifying_key="",
        audience=None,
        issuer=None,
        jwk_url: str = None,
        leeway: float | int | timedelta = None,
        json_encoder: type[json.JSONEncoder] | None = DecimalEncoder,
    ) -> None:
        self.app = app
        self._validate_algorithm(algorithm)

        self.algorithm = algorithm
        self.signing_key = signing_key
        self.verifying_key = verifying_key
        self.audience = audience
        self.issuer = issuer

        self.jwks_client = PyJWKClient(jwk_url) if jwk_url else None

        self.leeway = leeway
        self.json_encoder = json_encoder

    def _validate_algorithm(self, algorithm) -> None:
        """
        Ensure that the nominated algorithm is recognized, and that cryptography is installed
        for those algorithms that require it
        """
        if algorithm not in self.ALLOWED_ALGORITHMS:
            raise TokenBackendError(f"Unrecognized algorithm type '{algorithm}'")

        if algorithm in algorithms.requires_cryptography and not algorithms.has_crypto:
            raise TokenBackendError(f"You must have cryptography installed to use {algorithm}.")

    def get_leeway(self) -> timedelta:
        if self.leeway is None:
            return timedelta(seconds=0)
        elif isinstance(self.leeway, int | float):
            return timedelta(seconds=self.leeway)
        elif isinstance(self.leeway, timedelta):
            return self.leeway
        else:
            raise TokenBackendError(
                f"Unrecognized type '{self.leeway}', 'leeway' must be of type int, float "
                f"or timedelta.",
            )

    def get_verifying_key(self, token):
        if self.algorithm.startswith("HS"):
            return self.signing_key

        if self.jwks_client:
            try:
                return self.jwks_client.get_signing_key_from_jwt(token).key
            except PyJWKClientError as ex:
                raise TokenBackendError("Token is invalid or expired") from ex

        return self.verifying_key

    def encode(self, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        jwt_payload = payload.copy()
        if self.audience is not None:
            jwt_payload["aud"] = self.audience
        if self.issuer is not None:
            jwt_payload["iss"] = self.issuer

        token = jwt.encode(
            jwt_payload,
            self.signing_key,
            algorithm=self.algorithm,
            json_encoder=self.json_encoder,
        )
        if isinstance(token, bytes):
            # For PyJWT <= 1.7.1
            return token.decode("utf-8")
        # For PyJWT >= 2.0.0a1
        return token

    def decode(self, token, verify=True):
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            return jwt.decode(
                token,
                self.get_verifying_key(token),
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
                leeway=self.get_leeway(),
                options={
                    "verify_aud": self.audience is not None,
                    "verify_signature": verify,
                },
            )
        except InvalidAlgorithmError as ex:
            raise TokenBackendError("Invalid algorithm specified") from ex
        except InvalidTokenError as ex:
            raise TokenBackendError("Token is invalid or expired") from ex


async def setup(app):
    return app.add_client(TokenBackend(app, "HS256", Config().SECRET_KEY))
