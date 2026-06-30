from collections.abc import Callable, Iterator
from typing import Any, ClassVar, overload


class FlagValue:
    def __init__(self, func: Callable[[Any], int]) -> None:
        self.flag: int = func(None)
        self.__doc__: str | None = func.__doc__

    @overload
    def __get__(self, instance: None, owner): ...

    @overload
    def __get__(self, instance, owner) -> bool: ...

    def __get__(self, instance, owner) -> Any:
        if instance is None:
            return self
        return instance._has_flag(self.flag)

    def __set__(self, instance, value: bool) -> None:
        instance._set_flag(self.flag, value)

    def __repr__(self) -> str:
        return f"<flag_value flag={self.flag!r}>"


class AliasFlagValue(FlagValue):
    pass


def fill_with_flags(*, inverted: bool = False):
    def decorator(cls):
        # fmt: off
        cls.VALID_FLAGS = {
            name: value.flag
            for name, value in cls.__dict__.items()
            if isinstance(value, FlagValue)
        }
        # fmt: on

        if inverted:
            max_bits = max(cls.VALID_FLAGS.values()).bit_length()
            cls.DEFAULT_VALUE = -1 + (2**max_bits)
        else:
            cls.DEFAULT_VALUE = 0

        return cls

    return decorator


# n.b. flags must inherit from this and use the decorator above
class BaseFlags:
    VALID_FLAGS: ClassVar[dict[str, int]]
    DEFAULT_VALUE: ClassVar[int]

    value: int

    __slots__ = ("value",)

    def __init__(self, **kwargs: bool) -> None:
        self.value = self.DEFAULT_VALUE
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid flag name.")
            setattr(self, key, value)

    @classmethod
    def _from_value(cls, value: int):
        self = cls.__new__(cls)
        self.value = value
        return self

    def __or__(self, other):
        return self._from_value(self.value | other.value)

    def __and__(self, other):
        return self._from_value(self.value & other.value)

    def __xor__(self, other):
        return self._from_value(self.value ^ other.value)

    def __ior__(self, other):
        self.value |= other.value
        return self

    def __iand__(self, other):
        self.value &= other.value
        return self

    def __ixor__(self, other):
        self.value ^= other.value
        return self

    def __invert__(self):
        max_bits = max(self.VALID_FLAGS.values()).bit_length()
        max_value = -1 + (2**max_bits)
        return self._from_value(self.value ^ max_value)

    def __bool__(self) -> bool:
        return self.value != self.DEFAULT_VALUE

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} value={self.value}>"

    def __iter__(self) -> Iterator[tuple[str, bool]]:
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, AliasFlagValue):
                continue

            if isinstance(value, FlagValue):
                yield (name, self._has_flag(value.flag))

    def _has_flag(self, o: int) -> bool:
        return (self.value & o) == o

    def _set_flag(self, o: int, toggle: bool) -> None:
        if toggle is True:
            self.value |= o
        elif toggle is False:
            self.value &= ~o
        else:
            raise TypeError(f"Value to set for {self.__class__.__name__} must be a bool.")


class PermissionAlias(AliasFlagValue):
    alias: str


def make_permission_alias(alias: str) -> Callable[[Callable[[Any], int]], PermissionAlias]:
    def decorator(func: Callable[[Any], int]) -> PermissionAlias:
        ret = PermissionAlias(func)
        ret.alias = alias
        return ret

    return decorator


@fill_with_flags()
class Permissions(BaseFlags):
    __slots__ = ()

    def __init__(self, permissions: int = 0, **kwargs: bool) -> None:
        if not isinstance(permissions, int):
            raise TypeError(
                f"Expected int parameter, received {permissions.__class__.__name__} instead.",
            )

        self.value = permissions
        for key, value in kwargs.items():
            try:
                flag = self.VALID_FLAGS[key]
            except KeyError:
                raise TypeError(f"{key!r} is not a valid permission name.") from None
            else:
                self._set_flag(flag, value)

    def is_subset(self, other) -> bool:
        """Returns ``True`` if self has the same or fewer permissions as other."""
        if isinstance(other, Permissions):
            return (self.value & other.value) == self.value
        else:
            raise TypeError(
                f"cannot compare {self.__class__.__name__} with {other.__class__.__name__}",
            )

    def is_superset(self, other) -> bool:
        """Returns ``True`` if self has the same or more permissions as other."""
        if isinstance(other, Permissions):
            return (self.value | other.value) == self.value
        else:
            raise TypeError(
                f"cannot compare {self.__class__.__name__} with {other.__class__.__name__}",
            )

    def is_strict_subset(self, other) -> bool:
        """Returns ``True`` if the permissions on other are a strict subset of those on self."""
        return self.is_subset(other) and self != other

    def is_strict_superset(self, other) -> bool:
        """Returns ``True`` if the permissions on other are a strict superset of those on self."""
        return self.is_superset(other) and self != other

    __le__ = is_subset
    __ge__ = is_superset
    __lt__ = is_strict_subset
    __gt__ = is_strict_superset

    @classmethod
    def none(cls):
        """A factory method that creates a :class:`Permissions` with all
        permissions set to ``False``."""
        return cls(0)

    def update(self, **kwargs: bool) -> None:
        r"""Bulk updates this permission object.

        Allows you to set multiple attributes by using keyword
        arguments. The names must be equivalent to the properties
        listed. Extraneous key/value pairs will be silently ignored.

        Parameters
        ------------
        \*\*kwargs
            A list of key/value pairs to bulk update permissions with.
        """
        for key, value in kwargs.items():
            flag = self.VALID_FLAGS.get(key)
            if flag is not None:
                self._set_flag(flag, value)

    def handle_overwrite(self, allow: int, deny: int) -> None:
        # Basically this is what's happening here.
        # We have an original bit array, e.g. 1010
        # Then we have another bit array that is 'denied', e.g. 1111
        # And then we have the last one which is 'allowed', e.g. 0101
        # We want original OP denied to end up resulting in
        # whatever is in denied to be set to 0.
        # So 1010 OP 1111 -> 0000
        # Then we take this value and look at the allowed values.
        # And whatever is allowed is set to 1.
        # So 0000 OP2 0101 -> 0101
        # The OP is base  & ~denied.
        # The OP2 is base | allowed.
        self.value: int = (self.value & ~deny) | allow

    @FlagValue
    def asset_type_category_create(self) -> int:
        return 1 << 0

    @FlagValue
    def asset_type_category_update(self) -> int:
        return 1 << 1

    @FlagValue
    def asset_type_category_read(self) -> int:
        return 1 << 2

    @FlagValue
    def asset_type_category_delete(self) -> int:
        return 1 << 3

    @FlagValue
    def asset_type_create(self) -> int:
        return 1 << 4

    @FlagValue
    def asset_type_update(self) -> int:
        return 1 << 5

    @FlagValue
    def asset_type_read(self) -> int:
        return 1 << 6

    @FlagValue
    def asset_type_delete(self) -> int:
        return 1 << 7

    @FlagValue
    def asset_create(self) -> int:
        return 1 << 8

    @FlagValue
    def asset_update(self) -> int:
        return 1 << 9

    @FlagValue
    def asset_read(self) -> int:
        return 1 << 10

    @FlagValue
    def asset_delete(self) -> int:
        return 1 << 11

    @FlagValue
    def typeplate_update(self) -> int:
        return 1 << 12

    @FlagValue
    def typeplate_read(self) -> int:
        return 1 << 13

    @FlagValue
    def service_create(self) -> int:
        return 1 << 14

    @FlagValue
    def service_update(self) -> int:
        return 1 << 15

    @FlagValue
    def service_read(self) -> int:
        return 1 << 16

    @FlagValue
    def service_delete(self) -> int:
        return 1 << 17

    @FlagValue
    def organization_create(self) -> int:
        return 1 << 18

    @FlagValue
    def organization_update(self) -> int:
        return 1 << 19

    @FlagValue
    def organization_read(self) -> int:
        return 1 << 20

    @FlagValue
    def organization_delete(self) -> int:
        return 1 << 21

    @FlagValue
    def user_create(self) -> int:
        return 1 << 22

    @FlagValue
    def user_update(self) -> int:
        return 1 << 23

    @FlagValue
    def user_read(self) -> int:
        return 1 << 24

    @FlagValue
    def user_delete(self) -> int:
        return 1 << 25

    @FlagValue
    def org_user_delete(self) -> int:
        return 1 << 26

    @FlagValue
    def change_user_password(self) -> int:
        return 1 << 27

    @FlagValue
    def update_location(self) -> int:
        return 1 << 28

    @FlagValue
    def get_location(self) -> int:
        return 1 << 29

    @FlagValue
    def get_role(self) -> int:
        return 1 << 30

    @FlagValue
    def create_role(self) -> int:
        return 1 << 31

    @FlagValue
    def list_asset_pass(self) -> int:
        return 1 << 32

    @FlagValue
    def audit_create(self) -> int:
        return 1 << 33

    @FlagValue
    def audit_read(self) -> int:
        return 1 << 34

    @FlagValue
    def audit_update(self) -> int:
        return 1 << 35

    @FlagValue
    def audit_delete(self) -> int:
        return 1 << 36

    @FlagValue
    def instruction_manual_create(self) -> int:
        return 1 << 37

    @FlagValue
    def instruction_manual_read(self) -> int:
        return 1 << 38

    @FlagValue
    def instruction_manual_update(self) -> int:
        return 1 << 39

    @FlagValue
    def instruction_manual_delete(self) -> int:
        return 1 << 40

    @FlagValue
    def typeplate_document_delete(self) -> int:
        return 1 << 41
