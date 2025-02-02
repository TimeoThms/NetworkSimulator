from Interfaces import Interface
from IpUtils import IPv4
from Packet import Packet


class Device:
    def __init__(self, name: str, interfaces: dict[str, Interface] = None):
        self.name = name
        self.interfaces = interfaces
        # self.arp_table = {}

    def arp_request(self, interface, target_ip):
        """Returns the MAC Adress of in interface with the specified IPv4 on the same subnet"""
        if target_ip in self.interfaces[interface.name].arp_table:
            return self.interfaces[interface.name].arp_table[target_ip]

        if interface.connected_to:
            target_device = interface.connected_to.device

            # Handle the ARP request if the device is connected to a Switch
            if isinstance(target_device, Switch):
                response_mac = target_device.forward_arp_request(target_ip, interface.connected_to)

            # If not, direct query to the connected Device
            else:
                response_mac = target_device.arp_reply(target_ip)

            if response_mac:
                self.interfaces[interface.name].arp_table[target_ip] = response_mac
                # self.arp_table[target_ip] = response_mac
                return response_mac

    def arp_reply(self, target_ip: str):
        """Returns MAC adress if target_ip is and IPv4 of an interface on the Device"""
        for interface in self.interfaces.values():
            if interface.ipv4 == target_ip:
                return interface.mac
        return None


class Router(Device):
    def __init__(self, name: str, num_ports: int = 4):
        interfaces = {f"eth{i}": Interface(f"eth{i}", self) for i in range(num_ports)}
        super().__init__(name, interfaces)
        self.routing_table = dict()

    def transmit_packet(self, packet: Packet):
        destination_subnet = IPv4(packet.dest_ip).get_subnet()
        for network in self.routing_table:
            if IPv4(network).get_subnet() == destination_subnet:

                interface = self.routing_table[network]["interface"]
                self.arp_request(interface, packet.dest_ip)
                destination_mac = self.interfaces[interface.name].arp_table
                if destination_mac:
                    print(f"Packet sent to {packet.dest_ip} via interface {interface.name} and MAC {destination_mac}")
                    return

    def get_mac_from_arp_table(self, target_ip, interface):
        if target_ip in self.interfaces[interface.name].arp_table:
            return self.interfaces[interface.name].arp_table[target_ip]
        return None


class Switch(Device):
    def __init__(self, name: str, num_ports: int, interfaces: dict[str, Interface] = None):
        interfaces = {f"eth{i}": Interface(f"eth{i}", self) for i in range(num_ports)}
        super().__init__(name, interfaces)

    def forward_arp_request(self, target_ip: str, source_interface: Interface):
        """Forward the ARP Request to all the Devices connected to the Switch"""
        for interface in self.interfaces.values():
            if interface != source_interface and interface.connected_to:
                response = interface.connected_to.device.arp_reply(target_ip)
                if response:
                    return response
        return None


class Computer(Device):
    def __init__(self, name: str, gateway: str):
        interfaces = {"eth0": Interface("eth0", self), "eth1": Interface("eth1", self)}
        super().__init__(name, interfaces)
        self.gateway = gateway

    def send_packet(self, packet: Packet):
        """Sends a packet to the specified IPv4 adress"""
        # Handle packets if the source and destination are on the same subnet
        for interface in self.interfaces.values():
            if interface.ipv4 and IPv4(interface.ipv4).get_subnet() == IPv4(packet.dest_ip).get_subnet():
                print(f"Same subnet via {interface.name}")
                return
        # If the destination is not on the same subnet, use the default gateway
        for interface in self.interfaces.values():
            if interface.ipv4 and self.gateway and IPv4(interface.ipv4).get_subnet() == IPv4(
                    self.gateway).get_subnet():
                if interface.connected_to and interface.connected_to.ipv4 == self.gateway:
                    if isinstance(interface.connected_to.device, Router):
                        interface.connected_to.device.transmit_packet(packet)
                        return
                    else:
                        print("Gateway is not a Router!")
                else:
                    print("Unable to connect to the default gateway")
