import enum

from t2c_backend.core.i18n import _


class ENVIRONMENT(enum.StrEnum):
    TEST = "test"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    def __str__(self) -> str:
        return self.value


class ErrorMessageCodes(enum.StrEnum):
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXIST = "ALREADY_EXIST"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    GENERATE_ERROR = "GENERATE_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"


class TokenType(enum.IntEnum):
    EmailVerificationToken = 1
    ForgotPasswordToken = 2


class InputType(enum.StrEnum):
    time = "time"
    url = "url"
    text = "text"
    radio = "radio"
    password = "password"
    number = "number"
    image = "image"
    file = "file"
    email = "email"
    date = "date"
    datetime = "datetime"
    checkbox = "checkbox"
    multiselect = "multiselect"
    select = "select"


class Role(enum.StrEnum):
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


class Language(enum.StrEnum):
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


class DocumentStatus(enum.StrEnum):
    released = "released"
    pending = "pending"
    rejected = "rejected"


class DocumentType(enum.StrEnum):
    instruction_manual = "instruction_manual"
    inspection = "inspection"
    typeplate = "typeplate"
    declaration_file = "declaration_file"


class Status(enum.StrEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class AssetStatus(enum.StrEnum):
    putting_into_service = "putting_into_service"
    placing_on_the_market = "placing_on_the_market"
    making_available_on_the_market = "making_available_on_the_market"
    re_use = "re_use"
    repair = "repair"
    maintenance = "maintenance"
    remanufacturing = "remanufacturing"
    repurposing = "repurposing"
    treatment = "treatment"
    preparation_for_re_use = "preparation_for_re_use"
    preparation_for_repurposing = "preparation_for_repurposing"
    preparation_for_recycling = "preparation_for_recycling"
    recycling = "recycling"
    waste_management = "waste_management"


class UserStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    BANNED = "BANNED"


class SortBy(enum.StrEnum):
    Latest = "latest"
    Oldest = "oldest"


class ServiceTypes(enum.StrEnum):
    premium = "premium"
    basic = "basic"


class AuditTaskStatus(enum.StrEnum):
    PASSED = _("PASSED")
    FAILED = _("FAILED")
    CONDITIONAL = _("CONDITIONAL")


class TaskType(enum.StrEnum):
    audit = "audit"
    inspection = "inspection"

    def __str__(self) -> str:
        return self.value


class DocumentFor(enum.StrEnum):
    AuditTaskDocuments = "audit_task_documents"
    InstructionManualDocuments = "instruction_manual_documents"
    EuFiles = "eu_files"
    AssetTypeFieldSpecificDocuments = "asset_type_field_specific_documents"

    def __str__(self) -> str:
        return self.value
