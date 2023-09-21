import logging
import os
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
        self.url_base_download = f'{_download_url}bot{_token}'
        self.url_base = f'{_url}bot{_token}/'

    def process_messages(self):
        update_id = None
        while True:
            atualizacao = self.get_new_messages(update_id)
            dados = atualizacao["result"]
            if dados:
                for dado in dados:
                    update_id = dado["update_id"]
                    username = str(dado["message"]["from"]["first_name"])
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
                    

    def get_new_messages(self, update_id):
        link_req = f'{self.url_base}getUpdates?timeout=100'
        if update_id:
            link_req = f'{link_req}&offset={update_id + 1}'
        response = requests.get(link_req)
        return json.loads(response.content)

    def download_file(self, file):
        file_id = file["file_id"]
        link_req = f'{self.url_base}getFile?file_id={file_id}'
        response = requests.get(link_req)
        content = json.loads(response.content)
        file_path = str(content["result"]["file_path"])
        file_name = file_path.rsplit('/', 1)[1]

        link_req = f'{self.url_base_download}/{file_path}'
        file = requests.get(link_req)
        file_dir = f'./services/downloads/{file_name}'
        with open(file_dir, 'wb') as f:
            f.write(file.content)

        return file_dir

    def process_file(self, file, chat_id, username):
        '''Esse método irá orquestrar a sincronização e dar retornos ao usuário referente a cada etapa'''
        file_dir = self.download_file(file)

        logging.info(f"Iniciando importação solicitado pelo usuário: {username} via Telegram")

        self.response(f'Arquivo recebido com sucesso!', chat_id)
        self.response(f'Iniciando sincronização...', chat_id)

        self.response(f'Sincronizando redes [...]', chat_id)
        sync_netw = self.db.sync_network(file_dir)      
        self.response(f'Sincronizando redes [{sync_netw["status"]}]', chat_id)

        self.response(f'Sincronizando coordenadas [...]', chat_id)
        sync_coords = self.db.sync_location(file_dir)
        self.response(f'Sincronizando coordenadas [{sync_coords["status"]}]', chat_id)

        self.response(f'Sincronizando rotas [...]', chat_id)
        sync_routes = self.db.sync_route(file_dir)
        self.response(f'Sincronizando rotas [{sync_routes["status"]}]', chat_id)

        message = f'Sincronização finalizada com sucesso!'
        self.response(message, chat_id)

        message = f"""
        Foram adicionados:
        {sync_netw["changes"]} Novas redes
        {sync_coords["changes"]} Novas coordenadas
        {sync_routes["changes"]} Novas rotas    
        """
        self.response(message, chat_id)

        logging.info(f"Finalizado importação solicitado pelo usuário: {username} via Telegram: {message}")
        
        if isinstance(sync_netw, dict) and sync_netw["changes"] > 0:
            logging.info(f"Processando as redes novas...")
            self.vuln.check_vuln_pending_db(sync_netw["data"])
            return None

        logging.info(f"Nenhuma rede nova..")
        

    def response(self, message: str, chat_id: str):
        link_requisicao = f'{self.url_base}sendMessage?chat_id={chat_id}&text={message}'
        requests.get(link_requisicao)