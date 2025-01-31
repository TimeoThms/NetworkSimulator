from enum import Enum
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Devices import Device

existing_macs = set()


def generate_mac_address(vendor_prefix="00:50:4C"):
    while True:
        mac = vendor_prefix + ":" + ":".join([f"{random.randint(0, 255):02X}" for _ in range(3)])

        if mac not in existing_macs:
            existing_macs.add(mac)
            return mac


class LinkType(Enum):
    ETHERNET = 10
    FASTETHERNET = 100
    FIBRE = 1000


class Interface:
    def __init__(self, name: str, device: 'Device', mac: str = None, ipv4: str = None):
        self.name = name
        self.device = device
        if mac is None:
            mac = generate_mac_address()
        else:
            existing_macs.add(mac)
        self.mac = mac
        self.ipv4 = ipv4
        self.link_type = None
        self.connected_to = None

    def connect(self, interface: 'Interface', link_type: LinkType):
        self.connected_to = interface
        interface.connected_to = self
        self.link_type = link_type
        interface.link_type = link_type

    def disconnect(self):
        if self.connected_to is not None and isinstance(self.connected_to, Interface):
            self.connected_to.connected_to = None
            self.connected_to.link_type = None
            self.connected_to = None
            self.link_type = None

    def is_connected(self):
        if self.connected_to is not None:
            return True
        else:
            return False

# class Cable:
#     def __init__(self, cable_type: CableType):
#         self.cable_type = cable_type
#         self.interface1 = None
#         self.interface2 = None
