"""Eltex-specific patching logic for ``eltex.rul``.

Eltex shares the IOS ``switchport trunk allowed vlan`` vlan-list semantics with
Cisco, so the well-tested Cisco vlan-database processor is re-exported here
instead of being duplicated.  Keeping the vendor-facing path under
``annet.rulebook.eltex`` means the Eltex rulebook never depends on Cisco
internals directly and the behaviour can be specialised later without touching
other vendors.
"""

from annet.rulebook.cisco.vlandb import simple, swtrunk


__all__ = ["simple", "swtrunk"]
