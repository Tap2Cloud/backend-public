from enum import Enum


class ENVIRONMENT(str, Enum):
    TEST = "test"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    def __str__(self) -> str:
        return self.value


class ErrorMessageCodes(str, Enum):
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXIST = "ALREADY_EXIST"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    GENERATE_ERROR = "GENERATE_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"


class Language(str, Enum):
    en = "en"
    de = "de"

    @classmethod
    def from_value(cls, value) -> "Language":
        """
        Resolves a role from a string or integer value.
        Defaults to Role.User if the value is invalid.
        """
        if isinstance(value, str) and value in cls.__members__:
            return cls[value]
        return cls.en


class TokenType(int, Enum):
    EmailVerificationToken = 1
    ForgotPasswordToken = 2


class Status(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class Role(str, Enum):
    member = "Member"
    admin = "Admin"
    owner = "Owner"
    super_admin = "Super Admin"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def __iter__(cls):
        return cls.__members__.items()

    @classmethod
    def organization_roles(cls):
        """
        Iterates over all roles excluding 'super_admin'.
        Returns a generator of (name, value) tuples.
        """
        return (
            (name, role.value) for name, role in cls.__members__.items() if name != "super_admin"
        )

    @classmethod
    def from_value(cls, value) -> "Role":
        """
        Resolves a role from a string or integer value.
        Defaults to Role.User if the value is invalid.
        """
        if isinstance(value, str) and value in cls.__members__:
            return cls[value]
        elif isinstance(value, int) and value in cls._value2member_map_:
            return cls(value)
        return cls.member


class SortBy(str, Enum):
    Latest = "latest"
    Oldest = "oldest"
