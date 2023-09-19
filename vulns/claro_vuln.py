import re
from interfaces.vuln_interface import VulnInterface


class ClaroVuln(VulnInterface):

    def check_vuln(self, ssid) -> str:
        NET_regex = re.compile("^NET_.(g|G)")
        CLARO_regex = re.compile("^CLARO_")
        if NET_regex.search(ssid) or CLARO_regex.search(ssid) is not None:
            return True
        else:
            return False


    def compile_passw(self, ssid: str, mac: str) -> dict:
        chunks = [
    			"".join(mac.upper().split(":")[2:3]),
    			ssid.split("_")[1][2:]
             ]
        password = "".join(chunks)
        return {'ssid': ssid,'mac': mac,'password': password}
