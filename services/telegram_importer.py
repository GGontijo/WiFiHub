import logging
import time
from models.base_models import NewAccessPoint
from helpers.db_helper import DbHelper
from helpers.config_helper import Config
from vulns.vuln import Vuln
import requests
import json

class Telegram_Service:
    # TODO: Implementar bliblioteca pronta do telegram e uso do MarkdownV2

    def __init__(self, db: DbHelper):
        self.db = db
        self.vuln = Vuln(db)
        _config = Config()
        _config_data = _config.get_config("TELEGRAM_IMPORTER")
        _token = _config_data["TOKEN"]
        _url = _config_data["URL"]
        _download_url = _config_data["DOWNLOAD_URL"]
        self.update_id = None
        self.url_base = f'{_url}bot{_token}/'
        self.url_base_download = f'{_download_url}bot{_token}'
        self.url_update_messages = f'{self.url_base}getUpdates?timeout=100'

    def process_messages(self):
        while True:
            time.sleep(5)
            atualizacao = self.get_new_messages()
            dados = atualizacao
            if dados:
                for dado in dados["result"]:
                    self.update_id = dado["update_id"]
                    first_name = dado["message"]["from"]["first_name"]
                    last_name = dado["message"]["from"]["last_name"]
                    username = str(f'{first_name}{last_name}')
                    message = dado["message"]["text"] if "text" in dado["message"] else dado["message"]["document"]["file_name"]
                    logging.info(f"[Recebido via Telegram] [{username}]: {message}")
                    chat_id = dado["message"]["from"]["id"]
                    if "document" in dado["message"] and '.sqlite' in dado["message"]["document"]["file_name"]:
                        file = dado["message"]["document"]
                        self.process_file(file, chat_id, username)
                        continue
                    if "/start" in message:
                        response = f"""                   
                        /start - Para exibir esta mensagem
                        /wifi NOME_DA_REDE|MAC_DA_REDE      
                        """
                        self.response(response,chat_id)
                        continue
                    if "/compilar" in message:
                        try:
                            input_data = message.split("/compilar")[1].strip()
                            data_parts = input_data.split("|")
                            if len(data_parts) == 2:
                                ssid, mac = data_parts[0].strip(), data_parts[1].strip()
                                ap = NewAccessPoint(ssid=ssid, mac=mac)
                                compiled_ap = self.vuln.compile(ap)
                                if compiled_ap:
                                    response = f'Senha gerada com sucesso para a rede {compiled_ap.ssid}!'
                                    logging.info(f'[Enviado via Telegram] para [{username}]: {response}')
                                    self.response(response, chat_id, md=True)
                                    self.response(compiled_ap.password, chat_id)
                                else:
                                    response = f'Não foi possível gerar a senha para a rede {ssid}.'
                                    logging.info(f'[Enviado via Telegram] para [{username}]: {response}')
                                    self.response(response, chat_id)
                            else:
                                response = 'Favor encaminhar nome da rede e mac da rede neste formato: NOME_DA_REDE|MAC_DA_REDE. Exemplo: claro_a2e1d3|af:43:2f:ff:43:ab'
                                logging.info(f'[Enviado via Telegram] para [{username}]: {response}')
                                self.response(response, chat_id)
                        except IndexError:
                            response = 'Favor encaminhar nome da rede e mac da rede neste formato: NOME_DA_REDE|MAC_DA_REDE. Exemplo: claro_a2e1d3|af:43:2f:ff:43:ab'
                            logging.info(f'[Enviado via Telegram] para [{username}]: {response}')
                            self.response(response, chat_id)
                        continue
                    

    def get_new_messages(self):
        _link_update_offset = f'{self.url_update_messages}&offset={self.update_id + 1 if self.update_id is not None else None}'
        try:
            response = requests.get(_link_update_offset)
        except requests.ConnectionError as e:
            logging.error(f'Houve um erro ao se comunicar com api.telegram.org. Detalhes: {e}')     
            for _ in range(6):
                logging.warn(f'Realizando nova tentativa... {_} de 6')
                response = requests.get(_link_update_offset)
                if response.status_code == 200:
                    break
                time.sleep(5)
        return json.loads(response.content)

    def download_file(self, file):
        file_id = file["file_id"]
        link_req = f'{self.url_base}getFile?file_id={file_id}'
        response = requests.get(link_req)
        content = json.loads(response.content)
        file_path = str(content["result"]["file_path"])
        file_name = file_path.rsplit('/', 1)[1]

        link_req = f'{self.url_base_download}/{file_path}'
        file_req = requests.get(link_req)
        file_dir = f'./services/downloads/{file_name}'
        logging.info(f"[Arquivo recebido via Telegram]: [{file['file_name']}] salvo em {file_dir}")
        with open(file_dir, 'wb') as f:
            f.write(file_req.content)

        return file_dir

    def process_file(self, file, chat_id, username):
        '''Esse método irá orquestrar a sincronização e dar retornos ao usuário referente a cada etapa'''
        file_dir = self.download_file(file)

        logging.info(f"Iniciando importação solicitado pelo usuário: {username} via Telegram")

        self.response(f'Arquivo recebido com sucesso!', chat_id)
        self.response(f'Iniciando sincronização...', chat_id)

        self.response(f'Sincronizando redes [...]', chat_id)
        sync_netw = self.db.sync_network(file_dir, username) 
        message = f'Sincronizando redes [{sync_netw["status"]}]'     
        self.response(message, chat_id)
        logging.info(f'[Enviado via Telegram] para [{username}]: {message}')

        self.response(f'Sincronizando coordenadas [...]', chat_id)
        sync_coords = self.db.sync_location(file_dir, username)
        message = f'Sincronizando coordenadas [{sync_coords["status"]}]'
        self.response(message, chat_id)
        logging.info(f'[Enviado via Telegram] para [{username}]: {message}')

        self.response(f'Sincronizando rotas [...]', chat_id)
        sync_routes = self.db.sync_route(file_dir, username)
        message = f'Sincronizando rotas [{sync_routes["status"]}]'
        self.response(message, chat_id)
        logging.info(f'[Enviado via Telegram] para [{username}]: {message}')

        message = f'Sincronização finalizada com sucesso!'
        self.response(message, chat_id)

        processed_result = 0
        if isinstance(sync_netw, dict) and sync_netw["changes"] > 0:
            message = f'Processando as redes novas...'
            logging.info(f"Processando as redes novas...")
            self.response(message, chat_id)
            processed_result = self.vuln.check_vuln_pending_db(sync_netw["data"])

        message = f"""
        Foram sincronizados:
        {sync_netw["changes"]} Novas redes
        {processed_result} Novas redes vulneráveis
        {sync_coords["changes"]} Novas coordenadas
        {sync_routes["changes"]} Novas rotas  
        """
        self.response(message, chat_id)
        logging.info(f"Finalizado importação solicitado pelo usuário: {username} via Telegram: {message}")
        
        

    def response(self, message: str, chat_id: str):
        link_requisicao = f'{self.url_base}sendMessage?chat_id={chat_id}&text={message}'
        requests.get(link_requisicao)