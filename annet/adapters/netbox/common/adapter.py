from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from annet.annlib.netdev.views.hardware import HardwareView

from .manufacturer import KNOWN_BREEDS, get_breed, get_hw
from .models import FHRPGroup, FHRPGroupAssignment, Interface, IpAddress, NetboxDevice, Prefix


NetboxDeviceT = TypeVar("NetboxDeviceT", bound=NetboxDevice[Any, Any])
InterfaceT = TypeVar("InterfaceT", bound=Interface[Any, Any])
IpAddressT = TypeVar("IpAddressT", bound=IpAddress[Any])
PrefixT = TypeVar("PrefixT", bound=Prefix)
FHRPGroupT = TypeVar("FHRPGroupT", bound=FHRPGroup[Any])
FHRPGroupAssignmentT = TypeVar(
    "FHRPGroupAssignmentT",
    bound=FHRPGroupAssignment[Any],
)


def get_device_breed(device: NetboxDeviceT) -> str:
    # An explicit platform slug always wins: it is the field NetBox operators
    # use to pin the annet/Napalm driver, and it lets a single manufacturer
    # (e.g. Eltex, which ships both ESR routers and MES switches) expose more
    # than one breed.
    if platform := getattr(device, "platform", None):
        if slug := getattr(platform, "slug", None):
            known = KNOWN_BREEDS
            if slug in known:
                return slug
    if device.device_type and device.device_type.manufacturer:
        return get_breed(
            device.device_type.manufacturer.name,
            device.device_type.model,
        )
    return ""


def get_device_hw(device: NetboxDeviceT) -> HardwareView:
    if device.device_type and device.device_type.manufacturer:
        return get_hw(
            device.device_type.manufacturer.name,
            device.device_type.model,
            device.platform.name if device.platform else "",
        )
    return HardwareView("", "")


class NetboxAdapter(
    ABC,
    Generic[
        NetboxDeviceT,
        InterfaceT,
        IpAddressT,
        PrefixT,
        FHRPGroupT,
        FHRPGroupAssignmentT,
    ],
):
    @abstractmethod
    def list_fqdns(self, query: dict[str, list[str]] | None = None) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def list_devices(self, query: dict[str, list[str]]) -> list[NetboxDeviceT]:
        raise NotImplementedError()

    @abstractmethod
    def get_device(self, device_id: int) -> NetboxDeviceT:
        raise NotImplementedError()

    @abstractmethod
    def list_interfaces_by_devices(self, device_ids: list[int]) -> list[InterfaceT]:
        raise NotImplementedError()

    @abstractmethod
    def list_interfaces(self, ids: list[int]) -> list[InterfaceT]:
        raise NotImplementedError()

    @abstractmethod
    def list_ipaddr_by_ifaces(self, iface_ids: list[int]) -> list[IpAddressT]:
        raise NotImplementedError()

    @abstractmethod
    def list_ipprefixes(self, prefixes: list[str]) -> list[PrefixT]:
        raise NotImplementedError()

    @abstractmethod
    def list_fhrp_group_assignments(
        self,
        iface_ids: list[int],
    ) -> list[FHRPGroupAssignmentT]:
        raise NotImplementedError()

    @abstractmethod
    def list_fhrp_groups(
        self,
        ids: list[int],
    ) -> list[FHRPGroupT]:
        raise NotImplementedError()
