import functools
import json
import re
from calendar import timegm
from datetime import UTC, datetime
from inspect import isawaitable

import tomlkit

from t2c_backend.core.db.session import get_session_context
from t2c_backend.schemas.v1.asset_pass import ResolvedRef
from t2c_backend.utils.enums import Gs1Standards, Scheme
from t2c_backend.utils.errors import BadRequestError


async def maybe_coroutine(func, *args, **kwargs):
    value = func(*args, **kwargs)
    if isawaitable(value):
        return await value
    else:
        return value


def _is_submodule(parent: str, child: str) -> bool:
    return parent == child or child.startswith(parent + ".")


def get_project_meta(file):
    with open(file) as pyproject:
        file_contents = pyproject.read()

    return tomlkit.parse(file_contents)["project"]


async def json_or_text(response):
    text = await response.text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    return text


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def aware_utcnow():
    return datetime.now(UTC)


def datetime_from_epoch(ts):
    return datetime.fromtimestamp(ts, tz=UTC)


def get_name_from_email(email: str) -> str | None:
    return (match := re.match(r"^[a-zA-Z]+", email.split("@")[0])) and match.group()


def r_getattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


class DictContainer(dict):
    """
    A custom container for services that allows attribute-style access.
    """

    def __init__(self, package_type, session_based=False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.package_type = package_type
        self.session_based = session_based

    def __getattr__(self, name):
        if self.session_based:
            session_id = get_session_context()
            if session_id not in self:
                raise AttributeError(f"'{session_id}' not found.")
            if name in self[session_id]:
                return self[session_id][name]
            raise AttributeError(f"{self.package_type} '{name}' not found in {session_id} session.")
        if name in self:
            return self[name]
        raise AttributeError(f"{self.package_type} '{name}' not found.")

    def __setattr__(self, name, value) -> None:
        if name == "package_type" or name == "session_based":
            # Avoid overwriting the package_type or session_based as a key in the dictionary
            super().__setattr__(name, value)
        else:
            self[name] = value

    def add_package(self, package_name, package, session_id):
        self[session_id] = {package_name: package, **self.get(session_id, {})}

    def remove_session(self, session_id):
        if self.session_based:
            self.pop(session_id, None)
            return
        raise AttributeError(":remove_session: not supported for this container")


def underscore(word: str) -> str:
    """
    Make an underscored, lowercase form from the expression in the string.

    Example::

        >>> underscore("DeviceType")
        'device_type'

    As a rule of thumb you can think of :func:`underscore` as the inverse of
    :func:`camelize`, though there are cases where that does not hold::

        >>> camelize(underscore("IOError"))
        'IoError'

    """
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", word)
    word = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", word)
    word = word.replace("-", "_")
    return word.lower()


def get_full_name(first_name, last_name):
    return f"{first_name} {last_name}".strip()


def gtin_check_digit(first13: str) -> int:
    """Mod-10, alternating weights 3/1 from the right."""
    total = 0
    for i, ch in enumerate(reversed(first13)):
        total += int(ch) * (3 if i % 2 == 0 else 1)
    return (10 - (total % 10)) % 10


def is_valid_gtin(gtin: str) -> bool:
    return len(gtin) == 14 and gtin.isdigit() and int(gtin[-1]) == gtin_check_digit(gtin[:13])


def parse_pairs(gs1_path: str) -> list[tuple[str, str]]:
    """'/01/x/21/y' -> [('01', 'x'), ('21', 'y')]. Path must be (AI, value) pairs."""
    segs = [s for s in gs1_path.strip("/").split("/") if s]
    if not segs or len(segs) % 2 != 0:
        raise BadRequestError("malformed GS1 Digital Link path")
    return [(segs[i], segs[i + 1]) for i in range(0, len(segs), 2)]


def interpret(gs1_path: str) -> ResolvedRef:
    """Turn a raw path into a scheme + the token to look up."""
    pairs = parse_pairs(gs1_path)
    ai_map = dict(pairs)  # AIs are unique within a valid DL URI
    primary_ai, primary_value = pairs[0]

    if primary_ai == str(Gs1Standards.AI_GTIN):
        if not is_valid_gtin(primary_value):
            raise BadRequestError("invalid GTIN (length or check digit)")
        serial = ai_map.get(str(Gs1Standards.AI_SERIAL))
        if not serial:
            raise BadRequestError("GTIN asset requires a serial (AI 21)")
        return ResolvedRef(scheme=Scheme.GTIN, token=serial, gtin=primary_value)

    if primary_ai == str(Gs1Standards.AI_GIAI):
        # GIAI is unit-level on its own — no serial qualifier expected.
        return ResolvedRef(scheme=Scheme.GIAI, token=primary_value)

    raise BadRequestError(f"unsupported primary identifier '{primary_ai}'")
