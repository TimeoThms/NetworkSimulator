from Interfaces import Interface
from IpUtils import IPv4
from Packet import Packet


class Device:
    def __init__(self, name: str, interfaces: dict[str, Interface] = None):
        self.name = name
        self.interfaces = interfaces

    def arp_request(self, interface, target_ip):
        """Returns the MAC Address of in interface with the specified IPv4 on the same subnet"""
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
        """Returns MAC address if target_ip is and IPv4 of an interface on the Device"""
        for interface in self.interfaces.values():
            if interface.ipv4 == target_ip:
                return interface.mac
        return None

    def handle_packet(self, packet: Packet):
        if packet.protocol != "ARP":
            for interface in self.interfaces.values():
                if packet.dest_mac == interface.mac:
                    print(f"{self.name} - Received packet from {packet.src_ip} on interface {interface.name}")
                    return
                if isinstance(self, Router):
                    self.transmit_packet(packet)
                    return
                if isinstance(self, Switch):
                    self.forward_packet(packet, interface)
                    return
        else:
            pass



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
                destination_mac = self.interfaces[interface.name].arp_table[packet.dest_ip]
                if destination_mac:
                    print(f"Packet sent to {packet.dest_ip} via interface {interface.name} and MAC {destination_mac}")
                    packet.dest_mac = destination_mac
                    interface.connected_to.device.handle_packet(packet)
                    return

    def get_mac_from_arp_table(self, target_ip, interface):
        if target_ip in self.interfaces[interface.name].arp_table:
            return self.interfaces[interface.name].arp_table[target_ip]
        return None


class Switch(Device):
    def __init__(self, name: str, num_ports: int):
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

    def forward_packet(self, packet: Packet, src_iface: Interface):
        """Forward a Packet through the Switch"""
        for interface in self.interfaces.values():
            if interface.connected_to and src_iface != interface and interface.connected_to.mac == packet.dest_mac:
                print(f"{self.name} - Packet forwarded directly to destination ({packet.dest_ip}) via interface {interface.name}")
                interface.connected_to.device.handle_packet(packet)
                return
        else:
            # Forward packet to all ports
            for interface in self.interfaces.values():
                print(f"{self.name} - Forwarding packet to all ports...")
                if interface.connected_to and src_iface != interface:
                    print(f"Forwarding to {interface.name}")
                    interface.connected_to.device.handle_packet(packet)
            return


class Computer(Device):
    def __init__(self, name: str, gateway: str):
        interfaces = {"eth0": Interface("eth0", self), "eth1": Interface("eth1", self)}
        super().__init__(name, interfaces)
        self.gateway = gateway

    def send_packet(self, packet: Packet):
        """Sends a packet to the specified IPv4 address"""
        # Handle packets if the source and destination are on the same subnet
        for interface in self.interfaces.values():
            if interface.ipv4 and IPv4(interface.ipv4).get_subnet() == IPv4(packet.dest_ip).get_subnet():
                #print(f"Same subnet via {interface.name}")
                if packet.dest_ip in interface.arp_table.keys():
                    packet.dest_mac = interface.arp_table[packet.dest_ip]
                else:
                    self.arp_request(interface, packet.dest_ip)
                    if packet.dest_ip in interface.arp_table.keys():
                        packet.dest_mac = interface.arp_table[packet.dest_ip]
                    else:
                        print(f"{self.name} - Unable to resolve destination MAC Address")
                        return
                interface.connected_to.device.handle_packet(packet)
                return
        # If the destination is not on the same subnet, use the default gateway
        for interface in self.interfaces.values():
            if interface.ipv4 and self.gateway and IPv4(interface.ipv4).get_subnet() == IPv4(
                    self.gateway).get_subnet():
                if interface.connected_to and interface.connected_to.ipv4 == self.gateway:
                    interface.connected_to.device.handle_packet(packet)
                else:
                    print("Unable to connect to the default gateway")
