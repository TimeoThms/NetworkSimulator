from enum import Enum

class LinkType(Enum):
    ETHERNET = 10
    FASTETHERNET = 100
    FIBRE = 1000

class Interface:
    def __init__(self, mac: str):
        self.mac = mac