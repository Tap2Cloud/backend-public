import functools
import json
import re
import unicodedata
from calendar import timegm
from datetime import UTC, datetime
from inspect import isawaitable

import tomlkit

from t2c_backend.core.db.session import get_session_context


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


# Characters that render as nothing and would otherwise make two identical names look different:
# soft hyphen, zero width space/non-joiner/joiner, bidi marks, word joiner and BOM.
INVISIBLE_CHARACTERS = r"[\u00ad\u200b-\u200f\u2060\ufeff]"
_INVISIBLE_CHARACTERS_RE = re.compile(INVISIBLE_CHARACTERS)
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_name(name: str) -> str:
    """
    Canonical form of a user supplied name.

    Applies NFKC (so fullwidth/compatibility characters and decomposed accents collapse onto
    their canonical form), drops zero-width characters, squashes every whitespace run into a
    single space and trims the ends. The result is what gets stored and what duplicate checks
    are compared on.
    """
    name = unicodedata.normalize("NFKC", name)
    name = _INVISIBLE_CHARACTERS_RE.sub("", name)
    return _WHITESPACE_RE.sub(" ", name).strip()


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
