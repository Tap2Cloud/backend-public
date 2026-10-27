"""
Merge the core translations into a downstream project's catalogs.

A downstream project keeps its own ``<locales>/<lang>/LC_MESSAGES/messages.po`` and
compiles a single ``messages.mo`` from it, so the core's messages are copied in first:

    python -m t2c_backend.core.i18n.sync path/to/your/locales
    pybabel compile -d path/to/your/locales -D messages

Entries copied from the core carry the ``CORE_MARKER`` auto comment and are refreshed on
every run, so changes made here reach the downstream catalogs. Entries without the marker
belong to the downstream project and take precedence over a core entry with the same msgid.
"""

import argparse
import sys
from pathlib import Path

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po

CORE_LOCALES_DIR = Path(__file__).resolve().parents[2] / "locales"
CORE_MARKER = "t2c_backend"
DOMAIN = "messages"


def _read_catalog(path: Path, locale: str) -> Catalog:
    if not path.exists():
        # Babel marks new catalogs fuzzy by default, and `pybabel compile` skips those.
        return Catalog(locale=locale, fuzzy=False)
    with path.open("rb") as file:
        return read_po(file, locale=locale)


def sync_catalogs(target_dir: Path) -> list[Path]:
    """
    Copy every core catalog's messages into the matching catalog under target_dir.

    Args:
        target_dir (Path): The downstream locales directory.

    Returns:
        list[Path]: The downstream .po files that were written.
    """
    written = []
    for core_po in sorted(CORE_LOCALES_DIR.glob(f"*/LC_MESSAGES/{DOMAIN}.po")):
        locale = core_po.parents[1].name
        core = _read_catalog(core_po, locale)
        target_po = target_dir / locale / "LC_MESSAGES" / f"{DOMAIN}.po"
        target = _read_catalog(target_po, locale)

        # Drop what earlier runs copied, so removed or edited core messages don't linger.
        for message in list(target):
            if message.id and CORE_MARKER in message.auto_comments:
                target.delete(message.id, message.context)
        # `pybabel update` marks core messages obsolete, as they aren't in the downstream
        # sources; they are active again once re-added below.
        target.obsolete = {
            key: message
            for key, message in target.obsolete.items()
            if core.get(message.id, message.context) is None
        }

        for message in core:
            if not message.id or target.get(message.id, message.context) is not None:
                continue
            target.add(
                message.id,
                message.string,
                flags=message.flags,
                auto_comments=[CORE_MARKER],
                context=message.context,
            )

        target_po.parent.mkdir(parents=True, exist_ok=True)
        with target_po.open("wb") as file:
            write_po(file, target)
        written.append(target_po)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge the t2c_backend translations into your project's .po files."
    )
    parser.add_argument("locales_dir", type=Path, help="Your project's locales directory.")
    args = parser.parse_args()

    for path in sync_catalogs(args.locales_dir):
        sys.stdout.write(f"Updated {path}\n")


if __name__ == "__main__":
    main()
