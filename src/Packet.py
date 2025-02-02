class Packet:
    def __init__(self, src_ip, dest_ip, payload="", protocol="DATA", src_mac=None, dest_mac=None):
        self.src_ip = src_ip
        self.dest_ip = dest_ip
        self.src_mac = src_mac
        self.dest_mac = dest_mac
        self.protocol = protocol
        self.payload = payload