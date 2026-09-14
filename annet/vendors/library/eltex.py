from typing import Any, Iterable, Optional

from annet.annlib.command import Command, CommandList
from annet.annlib.netdev.views.hardware import HardwareView
from annet.vendors.base import AbstractVendor
from annet.vendors.registry import registry
from annet.vendors.tabparser import BlockExitFormatter, FormatterContext, block_wrapper


class EltexFormatter(BlockExitFormatter):
    """Formatter for Eltex ESR/MES running-config.

    Eltex configuration is stored as a flat, Cisco-like tree:

        hostname esr-1
        interface gigabitethernet 1/0/1
          description uplink
          switchport mode trunk
        router ospf 1
          router-id 10.0.0.1
          network 10.0.0.0 /24 area 0.0.0.0

    Blocks are terminated with ``exit`` (like IOS).  Unlike Huawei (whose block
    terminator ``quit`` never appears in a saved config) Eltex stores ``exit``
    inline, so the splitter has to strip block-exit markers while computing the
    indentation -- exactly as the IOS formatter does.
    """

    block_exit_command = "exit"

    def _split_indent(
        self, line: str, indent: int, block_exit_strings: list[str]
    ) -> tuple[list[str], int]:
        # See CiscoFormatter._split_indent: an explicit exit string from a nested
        # sub-mode (e.g. "exit-address-family") opens a new level and must be
        # tracked separately from the generic "exit".
        if line.strip() in block_exit_strings:
            indent -= 1
            block_exit_strings.remove(line.strip())
            return block_exit_strings, indent

        wrapped = list(self.block_exit(FormatterContext(current=(line.strip(), {}))))
        if len(wrapped) != 3 or not isinstance(wrapped[1], str) or wrapped[1] == self.block_exit_command:
            return block_exit_strings, indent

        indent += 1
        block_exit_strings.append(wrapped[1])
        return block_exit_strings, indent

    def split(self, text: str) -> list[str]:
        additional_indent = 0
        block_exit_strings = [self.block_exit_command]

        tree = self.split_remove_spaces(text)
        result: list[str] = []
        for item in tree:
            stripped = item.strip()
            is_block_exit = stripped in block_exit_strings
            block_exit_strings, new_indent = self._split_indent(item, additional_indent, block_exit_strings)
            # Drop the syntactic block-exit rows: they are re-emitted by the
            # formatter when patching, exactly like on IOS.
            if not is_block_exit:
                result.append(f"{' ' * additional_indent}{item}")
            additional_indent = new_indent

        return result

    def block_exit(self, context: Optional[FormatterContext]) -> Iterable[Any]:
        current = context and context.row or ""

        if current.startswith("address-family"):
            yield from block_wrapper("exit-address-family")
        else:
            yield from super().block_exit(context)


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
