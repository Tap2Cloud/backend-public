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
