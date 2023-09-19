import re
from interfaces.vuln_interface import VulnInterface


class VivoFibraVuln(VulnInterface):

    def check_vuln(self, ssid) -> bool:
        VIVOFIBRA_regex = re.compile("^VIVOFIBRA-")
        if VIVOFIBRA_regex.search(ssid) is not None:
            return True
        else:
            return False

    def compile_passw(self, ssid: str, mac: str) -> dict:
        password = mac.replace(":","").upper()[2:]
        return {'ssid': ssid,'mac': mac,'password': password}
