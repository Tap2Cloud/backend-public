from datetime import timedelta
from typing import Any
from uuid import uuid4

from pydantic import BaseModel

from t2c_backend.utils.errors import TokenBackendError, TokenError
from t2c_backend.utils.misc import aware_utcnow, datetime_from_epoch, datetime_to_epoch

USER_ID_FIELD = "id"

JTI_CLAIM = "jti"
TOKEN_TYPE_CLAIM = "token_type"

USER_ID_CLAIM = "user_id"
USER_ORGANIZATION_ID_CLAIM = "organization_id"
USER_LOCATION_ID_CLAIM = "location_id"
USER_ROLES_ID_CLAIM = "roles"


class Token:
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """

    token_type = None
    lifetime = None

    def __init__(self, token_backend, token=None, verify=True) -> None:
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        if self.token_type is None or self.lifetime is None:
            raise TokenError("Cannot create token with no type or lifetime")

        self.token = token
        self.current_time = aware_utcnow()

        self.token_backend = token_backend

        # Set up token
        if token is not None:
            # Decode token
            try:
                self.payload = self.token_backend.decode(token, verify=verify)
            except TokenBackendError:
                raise TokenError("Token is invalid or expired")

            if verify:
                self.verify()
        else:
            # New token.  Skip all the verification steps.
            self.payload = {TOKEN_TYPE_CLAIM: self.token_type}

            # Set "exp" and "iat" claims with default value
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)
            self.set_iat(at_time=self.current_time)

            # Set "jti" claim
            self.set_jti()

    def __getattr__(self, key):
        if key in self.payload:
            return self.payload[key]
        raise AttributeError(f"'{key}' not found.")

    def __repr__(self) -> str:
        return repr(self.payload)

    def __getitem__(self, key):
        return self.payload[key]

    def __setitem__(self, key, value) -> None:
        self.payload[key] = value

    def __delitem__(self, key) -> None:
        del self.payload[key]

    def __contains__(self, key) -> bool:
        return key in self.payload

    def get(self, key, default=None):
        return self.payload.get(key, default)

    def update_payload(self, payload: dict) -> None:
        self.payload.update(payload)

    def __str__(self) -> str:
        """
        Signs and returns a token as a base64 encoded string.
        """
        return self.token_backend.encode(self.payload)

    def verify(self) -> None:
        """
        Performs additional validation steps which were not performed when this
        token was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        # According to RFC 7519, the "exp" claim is OPTIONAL
        # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
        # correct behavior for authorization tokens, we require an "exp"
        # claim.  We don't want any zombie tokens walking around.
        self.check_exp()

        # If the defaults are not None then we should enforce the
        # requirement of these settings.As above, the spec labels
        # these as optional.
        if JTI_CLAIM is not None and JTI_CLAIM not in self.payload:
            raise TokenError("Token has no id")

        if TOKEN_TYPE_CLAIM is not None:
            self.verify_token_type()

    def verify_token_type(self) -> None:
        """
        Ensures that the token type claim is present and has the correct value.
        """
        try:
            token_type = self.payload[TOKEN_TYPE_CLAIM]
        except KeyError:
            raise TokenError("Token has no type")

        if self.token_type != token_type:
            raise TokenError("Token has wrong type")

    def set_jti(self) -> None:
        """
        Populates the configured jti claim of a token with a string where there
        is a negligible probability that the same string will be chosen at a
        later time.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.7
        """
        self.payload[JTI_CLAIM] = uuid4().hex

    def set_exp(self, claim="exp", from_time=None, lifetime=None) -> None:
        """
        Updates the expiration time of a token.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.4
        """
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[claim] = datetime_to_epoch(from_time + lifetime)

    def set_iat(self, claim="iat", at_time=None) -> None:
        """
        Updates the time at which the token was issued.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.6
        """
        if at_time is None:
            at_time = self.current_time

        self.payload[claim] = datetime_to_epoch(at_time)

    def check_exp(self, claim="exp", current_time=None) -> None:
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = self.current_time

        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise TokenError(f"Token has no '{claim}' claim")

        claim_time = datetime_from_epoch(claim_value)
        leeway = self.token_backend.get_leeway()
        if claim_time <= current_time - leeway:
            raise TokenError(f"Token '{claim}' claim has expired")

    @classmethod
    def for_user(cls, user, token_backend):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        user_id = getattr(user, USER_ID_FIELD)

        token = cls(token_backend)
        token[USER_ID_CLAIM] = user_id

        return token

    @property
    def user_id(self) -> int:
        """
        Returns the user ID from the token payload.
        """
        return self.get(USER_ID_CLAIM)

    @property
    def organization_id(self) -> int | None:
        """
        Returns the organization ID from the token payload.
        """
        return self.get(USER_ORGANIZATION_ID_CLAIM)

    @property
    def location_id(self) -> int | None:
        """
        Returns the organization ID from the token payload.
        """
        return self.get(USER_LOCATION_ID_CLAIM)

    @property
    def roles(self) -> list[dict[str, Any]]:
        """
        Returns the role from the token payload.
        """
        return self.get(USER_ROLES_ID_CLAIM, [])


class AccessToken(Token):
    token_type = "access"
    lifetime = timedelta(days=1)


class RefreshToken(Token):
    token_type = "refresh"
    lifetime = timedelta(days=7)


class TokenResponse(BaseModel):
    refresh_token: str
    access_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
