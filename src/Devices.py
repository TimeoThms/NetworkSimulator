from src.Interfaces import LinkType, Interface


class Device:
    def __init__(self, interfaces: list[LinkType]):
        self.interfaces = interfaces

class Router(Device):
    def __init__(self, interfaces: list[LinkType]):
        super().__init__(interfaces)

class Switch(Device):
    def __init__(self, num_ports: int, interfaces: list[LinkType]):
        super().__init__(interfaces)
        for i in range(num_ports):
            self.interfaces.append(Interface(f"0/{i}"))