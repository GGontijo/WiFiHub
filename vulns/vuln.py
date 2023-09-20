from typing import List
from helpers.db_helper import DbHelper
from interfaces.vuln_interface import VulnInterface
from models.base_models import NewAccessPoint
import importlib.util
import logging
import os, inspect
from web.map_helper import map_helper

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

    def check_vuln_all_db(self) -> None: # Processa redes pendentes
        vulns: int = 0
        ap_info_list: List[NewAccessPoint]
        ap_info_list = self.db.get_ap_mac()
        for ap in ap_info_list:
            if self.compile(ap):
                vulns += 1
            logging.info(f'Processado: {ap.ssid} | {ap.mac} - password: {ap.password}')
        logging.info(f'Total de {ap_info_list} processados. Total de {vulns} vulneráveis.')
        if vulns > 0:
            self.map = map_helper(self.db)
            logging.info('Mapa atualizado!')

    def check_vuln_pending_db(self) -> None: # Processa redes pendentes
        new_vulns: int = 0
        ap_info_list: List[NewAccessPoint]
        ap_info_list = self.db.get_pending_ap_mac()
        for ap in ap_info_list:
            if self.compile(ap):
                new_vulns += 1
            logging.info(f'Processado: {ap.ssid} | {ap.mac} - password: {ap.password}')
        logging.info(f'Foram processados {ap_info_list} redes. Total de {new_vulns} novas redes vulneráveis.')
        if new_vulns > 0:
            self.map = map_helper(self.db)
            logging.info('Mapa atualizado!')
    
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
                ap.password = v.compile_passw(ap.ssid,ap.mac)["password"]
                self.db.update_ap_passwd(ap)
                return True
        return False