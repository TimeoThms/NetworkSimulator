class IPv4:
    def __init__(self, ip: str):
        self.ip = ip
        ip_bytes = ip.split(".")
        mask = None
        if 1 <= int(ip_bytes[0]) <= 127:
            mask = "255.0.0.0"
        elif 128 <= int(ip_bytes[0]) <= 191:
            mask = "255.255.0.0"
        elif 192 <= int(ip_bytes[0]) <= 223:
            mask = "255.255.255.0"
        self.mask = mask

    def get_subnet(self):
        return '.'.join(str(byte) for byte in [
            int(ip_byte) & int(mask_byte)
            for ip_byte, mask_byte in zip(self.ip.split('.'), self.mask.split('.'))
        ])
