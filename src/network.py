from Devices import Computer, Router, Switch
from Interfaces import LinkType
from Packet import Packet

# PCs
pc1 = Computer("PC-01", "192.168.1.254")
pc1.interfaces["eth0"].ipv4 = "192.168.1.1"

pc2 = Computer("PC-02", "172.16.0.254")
pc2.interfaces["eth0"].ipv4 = "172.16.0.1"

# Switchs
s1 = Switch("Switch 1", 4)

# # Routers
r1 = Router("Router-01")
r1.interfaces["eth0"].ipv4 = "192.168.1.254"
r1.interfaces["eth1"].ipv4 = "172.16.0.254"


# Interfaces
pc1.interfaces["eth0"].connect(r1.interfaces["eth0"], LinkType.ETHERNET)
# pc2.interfaces["eth0"].connect(s1.interfaces["eth1"], LinkType.ETHERNET)
pc2.interfaces["eth0"].connect(r1.interfaces["eth1"], LinkType.FASTETHERNET)

r1.routing_table = {
    "192.168.1.0": {"interface": r1.interfaces["eth0"], "metric": 0},
    "172.16.0.0": {"interface": r1.interfaces["eth1"], "metric": 0}
}

pc1.send_packet(Packet("192.168.1.1", "172.16.0.1", "Hello"))