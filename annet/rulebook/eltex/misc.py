"""Eltex-specific patching helpers for ``eltex.rul``."""

from collections.abc import Iterator
from typing import Any

from annet.annlib.netdev.views.hardware import HardwareView
from annet.annlib.rulebook.common import default
from annet.annlib.types import Op


def _bare_reverse(row: str) -> Any:
    """Build a logic that negates a ``row ~`` rule with a bare ``no row``.

    The Eltex CLI clears parameterised rows such as ``description <value>``
    with a valueless ``no description``; passing the old value back is a
    syntax error.  Used for ``description`` (interfaces) and ``name`` (MES
    SVIs).
    """

    def _logic(
        rule: dict[str, Any],
        key: tuple[str, ...],
        diff: dict[str, list[dict[str, Any]]],
        hw: HardwareView,
        **_: Any,
    ) -> Iterator[tuple[bool, str, Any]]:
        if diff[Op.REMOVED] and not (diff[Op.ADDED] or diff[Op.AFFECTED]):
            yield (False, f"no {row}", None)
            return
        yield from default(rule, key, diff)

    return _logic


#: ``description ~ %logic=annet.rulebook.eltex.misc.description``
description = _bare_reverse("description")

#: ``name ~ %logic=annet.rulebook.eltex.misc.name`` (MES SVI names)
name = _bare_reverse("name")
