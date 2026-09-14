"""Validates that the Eltex deploy rulebook resolves interactive prompts.

No hardware is involved: we only compile the rulebook and match command paths
against it, exactly as ``annet deploy`` does before opening an SSH session.
"""

from types import SimpleNamespace

from annet.rulebook import deploying, get_rulebook


def _dialogs(rule):
    return [matcher.text for matcher in rule["attrs"]["dialogs"]]


def test_eltex_save_dialogs(ann_connectors):
    hw = SimpleNamespace()
    from annet.annlib.netdev.views.hardware import HardwareView

    hw = HardwareView("Eltex ESR-1000", "1.37.4")
    rules = get_rulebook(hw)["deploying"]

    rule = deploying.match_deploy_rule(rules, ("save",), {})
    texts = " ".join(_dialogs(rule)).lower()
    assert "ontinue" in texts
    assert "verwrite" in texts


def test_eltex_wildcard_safety_net(ann_connectors):
    from annet.annlib.netdev.views.hardware import HardwareView

    hw = HardwareView("Eltex MES-3300", "6.6.11.3")
    rules = get_rulebook(hw)["deploying"]

    # A command with no explicit deploy rule still gets the generic
    # "Continue? [y/N]" answers via the trailing "~" rule.
    rule = deploying.match_deploy_rule(rules, ("description foo",), {})
    texts = " ".join(_dialogs(rule)).lower()
    assert "ontinue" in texts
    assert "do you really" in texts

    # An explicit rule keeps its own dialogs rather than the wildcard's.
    rule = deploying.match_deploy_rule(rules, ("no vlan 20",), {})
    assert "ontinue" in " ".join(_dialogs(rule)).lower()
