from typing import List
from helpers.db_helper import DbHelper
from interfaces.vuln_interface import VulnInterface
from models.base_models import NewAccessPoint
import importlib.util
import logging
import os, inspect
from web.map_helper import Map_Helper

class Vuln:

    def __init__(self, db: DbHelper):
        self.map = Map_Helper(db)
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
            self.map.render()

    def check_vuln_pending_db(self, filtered_ap_list: List[NewAccessPoint] = None) -> str: # Processa redes pendentes
        new_vulns: int = 0
        ap_list: List[NewAccessPoint]
        if not filtered_ap_list: # Se não for passado ap's especificos, pegar o que não foi processado no banco
            logging.info('Iniciando processamento de todas as redes pendentes em banco')
            ap_list = self.db.get_pending_ap_mac()
        else:
            logging.info(f'Iniciando processamento de {len(filtered_ap_list)} novas redes adicionadas')
            ap_list = filtered_ap_list
        for ap in ap_list:
            if self.compile(ap):
                new_vulns += 1
                logging.info(f'Processado: {ap.ssid} | {ap.mac} - password: {ap.password}') 
        self.map.render()
        logging.info(f'Foram processados {len(ap_list)} redes. Total de {new_vulns} novas redes vulneráveis.')
        return new_vulns
    
    def check(self, ssid: str) -> bool:
        '''Valida se o AP é vulneravél á um dos scripts conhecidos'''
        for v in self.vulnerabilities:
            v: VulnInterface
            isvuln = v.check_vuln(ssid)
            if isvuln:
                return isvuln
        return False
    
    def compile(self, ap: NewAccessPoint):
        for v in self.vulnerabilities:
            v: VulnInterface
            if v.check_vuln(ap.ssid):
                ap.password = v.compile_passw(ap.ssid,ap.mac)["password"]
                self.db.update_ap_passwd(ap)
                return ap
        return None