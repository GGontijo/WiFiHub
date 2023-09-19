from helpers.db_helper import DbHelper
from interfaces.vuln_interface import VulnInterface
import importlib.util
import os, inspect

class Vuln:

    def __init__(self, db: DbHelper) -> None:
        self.db = db
        scripts_folder = './vulns'
        load_vuln = []
        self.vulnerabilities = []
        vuln_dir = os.listdir(scripts_folder)
        for vuln in vuln_dir:
            if vuln.endswith(".py") and vuln != ('vuln.py'):
                load_vuln.append(vuln)
        for i in load_vuln:
            script_name = i[:-3]
            scrpt_path = scripts_folder + '/' + i
            spec = importlib.util.spec_from_file_location(script_name, scrpt_path)
            specmodule = spec.loader.load_module()
            class_aux = inspect.getmembers(specmodule, inspect.isclass)[0]
            self.vulnerabilities.append(class_aux[1]())

    def check_vuln_db(self) -> None: #TODO: Considerar apenas redes sem senhas
        self.vuln_list = []
        ap_info = self.db.get_ap_mac()
        for ap in ap_info:
            for v in self.vulnerabilities:
                v: VulnInterface
                if v.check_vuln(ap['ssid']):
                    ap['vuln'] = v
                    self.vuln_list.append(ap)
        return self.vuln_list
    
    def check(self, ssid: str) -> bool:
        '''Valida se o AP é vulneravél á um dos scripts conhecidos'''
        for v in self.vulnerabilities:
            v: VulnInterface
            isvuln = v.check_vuln(ssid)
            if isvuln:
                return isvuln
        return False
    
    def compile(self, ssid: str, mac: str) -> str:
        for v in self.vulnerabilities:
            v: VulnInterface
            if v.check_vuln(ssid):
                passwd = v.compile_passw(ssid,mac)
                return passwd
        return False

    def get_pwned_passw(self) -> None:
        vuln_processed = []
        for vuln in self.vuln_list:
                vuln_aux = vuln['vuln']
                vuln_aux: VulnInterface
                passwd = vuln_aux.compile_passw(vuln['ssid'], vuln['mac'])
                vuln['password'] = passwd['password']
                vuln_processed.append(vuln)
        self.db.update_ap_passwd(vuln_processed)