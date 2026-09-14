"""Breed detection for NetBox devices, including the Eltex vendor."""

from types import SimpleNamespace

import pytest

from annet.adapters.netbox.common.adapter import get_device_breed, get_device_hw
from annet.adapters.netbox.common.manufacturer import KNOWN_BREEDS, get_breed


@pytest.mark.parametrize(
    "manufacturer, model, expected",
    [
        ("Eltex", "ESR-1000", "eltex"),
        ("Eltex", "ESR-1511", "eltex"),
        ("Eltex", "MES-2324", "eltex"),
        ("Eltex", "MES-3300", "eltex"),
        ("Huawei", "S5720", "vrp55"),
        ("Cisco", "Catalyst 2960", "ios12"),
        ("Arista", "7050QX-32", "eos4"),
    ],
)
def test_get_breed(manufacturer, model, expected):
    assert get_breed(manufacturer, model) == expected


def _device(manufacturer, model, platform_slug=None, platform_name=None):
    platform = None
    if platform_slug is not None or platform_name is not None:
        platform = SimpleNamespace(slug=platform_slug, name=platform_name or platform_slug)
    return SimpleNamespace(
        device_type=SimpleNamespace(manufacturer=SimpleNamespace(name=manufacturer), model=model),
        platform=platform,
    )


@pytest.mark.parametrize(
    "manufacturer, model, expected",
    [
        ("Eltex", "ESR-1000", "eltex"),
        ("Eltex", "MES-2324", "eltex"),
        ("Cisco", "Catalyst 2960", "ios12"),
    ],
)
def test_get_device_breed_from_manufacturer(manufacturer, model, expected):
    assert get_device_breed(_device(manufacturer, model)) == expected


def test_get_device_breed_platform_slug_wins():
    # An operator pins the annet driver via the platform slug; it overrides the
    # manufacturer/model heuristic.
    dev = _device("Eltex", "MES-2324", platform_slug="eltex")
    assert get_device_breed(dev) == "eltex"


def test_get_device_breed_unknown_platform_slug_falls_back():
    dev = _device("Eltex", "ESR-1000", platform_slug="some-custom-platform")
    assert get_device_breed(dev) == "eltex"


def test_get_device_hw_uses_platform_name():
    dev = _device("Eltex", "ESR-1000", platform_slug="esr", platform_name="esr-fw-1.37")
    hw = get_device_hw(dev)
    assert str(hw) == "Eltex.ESR.ESR1000"
    assert hw.soft == "esr-fw-1.37"


def test_known_breeds_contains_eltex():
    assert "eltex" in KNOWN_BREEDS
