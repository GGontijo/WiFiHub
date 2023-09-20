from typing import List
from helpers.db_helper import DbHelper
from interfaces.vuln_interface import VulnInterface
from models.base_models import NewAccessPoint
import importlib.util
import logging
import os, inspect

class Vuln:

    def __init__(self, db: DbHelper):
        self.db = db
        scripts_folder = os.path.abspath('./vulns')
        load_vuln = []
        self.vulnerabilities = []
        vuln_dir = os.listdir(scripts_folder)
        for vuln in vuln_dir:
            if vuln.endswith(".py") and vuln != ('vuln.py'):
                load_vuln.append(vuln)
        for i in load_vuln: # Carrega dinâmicamente as vulnerabilidades conhecidas
            script_name = i[:-3]
            script_path = scripts_folder + '/' + i
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            specmodule = spec.loader.load_module()
            class_aux = inspect.getmembers(specmodule, inspect.isclass)[0]
            self.vulnerabilities.append(class_aux[1]())

    def check_vuln_db(self) -> None: # Processa redes pendentes
        ap_info: List[NewAccessPoint]
        ap_info = self.db.get_ap_mac()
        for ap in ap_info:
            self.compile(ap)
            logging.info(f'Processado: {ap.ssid} | {ap.mac} - password: {ap.password}')
    
    def check(self, ssid: str) -> bool:
        '''Valida se o AP é vulneravél á um dos scripts conhecidos'''
        for v in self.vulnerabilities:
            v: VulnInterface
            isvuln = v.check_vuln(ssid)
            if isvuln:
                return isvuln
        return False
    
    def compile(self, ap: NewAccessPoint) -> bool:
        for v in self.vulnerabilities:
            v: VulnInterface
            if v.check_vuln(ap.ssid):
                ap.password = v.compile_passw(ap.ssid,ap.mac)
                self.db.update_ap_passwd(ap)
                return True
        return False