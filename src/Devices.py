from Interfaces import Interface
from IpUtils import IPv4


class Device:
    def __init__(self, name: str, interfaces: dict[str, Interface]):
        self.name = name
        self.interfaces = interfaces


class Router(Device):
    def __init__(self, name: str, num_ports: int = 4):
        interfaces = {f"eth{i}": Interface(f"eth{i}", self) for i in range(num_ports)}
        super().__init__(name, interfaces)
        self.routing_table = dict()

    def transmit_packet(self, destination: str, content: str = "Empty packet"):
        for network in self.routing_table:
            print(network)
            if IPv4(network).get_subnet() == IPv4(destination).get_subnet():
                print(f"Packet arrived in destination subnet. Used interface: {self.routing_table[network]['interface'].name}")
                return


class Switch(Device):
    def __init__(self, name: str, num_ports: int, interfaces: dict[str, Interface]):
        super().__init__(name, interfaces)
        self.interfaces = [Interface(f"eth{i}", self) for i in range(num_ports)]


class Computer(Device):
    def __init__(self, name: str, gateway: str):
        interfaces = {"eth0": Interface("eth0", self), "eth1": Interface("eth1", self)}
        super().__init__(name, interfaces)
        self.gateway = gateway

    def send_packet(self, destination: str, content: str = "Empty packet"):
        for interface in self.interfaces.values():
            if interface.ipv4 is not None and IPv4(interface.ipv4).get_subnet() == IPv4(destination).get_subnet():
                print(f"Same subnet via {interface.name}")
                return
        for interface in self.interfaces.values():
            if interface.ipv4 is not None and self.gateway is not None and IPv4(interface.ipv4).get_subnet() == IPv4(
                    self.gateway).get_subnet():
                print(f"Default gateway via {interface.name}")
                if interface.connected_to is not None and interface.connected_to.ipv4 == self.gateway:
                    if isinstance(interface.connected_to.device, Router):
                        interface.connected_to.device.transmit_packet(destination, content)
                        return
                    else:
                        print("Gateway is not a Router!")
                else:
                    print("Unable to connect to the default gateway")
