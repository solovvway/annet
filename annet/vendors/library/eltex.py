from typing import Any

from annet.annlib.command import Command, CommandList
from annet.annlib.netdev.views.hardware import HardwareView
from annet.vendors.base import AbstractVendor
from annet.vendors.registry import registry
from annet.vendors.tabparser import BlockExitFormatter


class EltexFormatter(BlockExitFormatter):
    """Formatter for Eltex ESR/MES running-config.

    Eltex configuration is stored as an indented, Cisco-like tree:

        hostname esr-1
        interface gigabitethernet 1/0/1
          description uplink
          switchport mode trunk
        router ospf 1
          router-id 10.0.0.1
          network 10.0.0.0 /24 area 0.0.0.0

    Every sub-mode is closed with a plain ``exit`` (there is no IOS-style
    ``exit-address-family``), and the device always writes ``show
    running-config`` fully indented.  The tree is therefore built directly from
    the leading whitespace of the (non-``exit``) rows, which works both for the
    device output and for the config rendered by the generators (which is
    indented but contains no ``exit`` rows).

    The generic ``exit`` is re-emitted by :meth:`BlockExitFormatter.block_exit`
    when patching, so dropping ``exit`` rows from the parsed tree is safe.
    """

    block_exit_command = "exit"

    def split(self, text: str) -> list[str]:
        # ``exit`` is a syntactic block terminator, not a configuration row, so
        # it must not enter the tree.  Indentation of the remaining rows is
        # preserved as-is; ``parse_to_tree`` derives the nesting from it.
        return [line for line in self.split_remove_spaces(text) if line.strip() != self.block_exit_command]


@registry.register
class EltexVendor(AbstractVendor):
    NAME = "eltex"

    def apply(
        self, hw: HardwareView, do_commit: bool, do_finalize: bool, path: str | None
    ) -> tuple[CommandList, CommandList]:
        before, after = CommandList(), CommandList()

        # Eltex ESR/MES stages configuration changes and applies them with an
        # explicit transaction: `do commit` inside the configure session applies
        # the staged config, `save` persists it to the startup config.
        #
        # The commit-confirm workflow (a timed rollback unless `do confirm` is
        # issued) is intentionally NOT triggered here: it is a separate operator
        # decision driven by the NetOps service / CLI, not by a plain deploy.
        before.add_cmd(Command("configure"))
        if do_commit:
            after.add_cmd(Command("do commit", timeout=60))
        if do_finalize:
            after.add_cmd(Command("save", timeout=60))
        after.add_cmd(Command("exit"))

        return before, after

    def match(self) -> list[str]:
        return ["Eltex"]

    @property
    def reverse(self) -> str:
        return "no"

    @property
    def hardware(self) -> HardwareView:
        return HardwareView("Eltex")

    def svi_name(self, num: int) -> str:
        return f"vlan {num}"

    def make_formatter(self, **kwargs: Any) -> EltexFormatter:
        return EltexFormatter(**kwargs)

    @property
    def exit(self) -> str:
        return "exit"
