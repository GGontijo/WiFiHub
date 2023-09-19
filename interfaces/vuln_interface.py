from abc import ABC, abstractmethod

class VulnInterface(ABC):

    @abstractmethod
    def check_vuln(ssid: str) -> bool:
        pass

    @abstractmethod
    def compile_passw(ssid: str, mac: str) -> dict:
        pass