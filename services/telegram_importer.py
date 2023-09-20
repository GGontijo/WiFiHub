import logging
from database.sqlite import SQLite
from helpers.db_helper import DbHelper
from helpers.config_helper import Config
from vulns.vuln import Vuln
import requests
import json

class Telegram_Service:

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
                    username = str(dado["message"]["from"]["username"])
                    chat_id = dado["message"]["from"]["id"]
                    if "document" not in dado["message"]:
                        message = f"Por favor {username}, me envie somente arquivos SQLite para sincronização do banco :D"
                        self.response(message, chat_id)
                        continue
                    file = dado["message"]["document"]

                    
                    self.process_file(file, chat_id, username)


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
        '''Esse método irá orquestrar a sincronização e dar retornos ao usuário referente a cada etapa, não gerando os logs'''
        file_dir = self.download_file(file)

        logging.info(f"Iniciando processamento solicitado pelo usuário: {username} via Telegram")

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

        logging.info(f"Finalizado processamento solicitado pelo usuário: {username} via Telegram. Foram adicionadas {sync_netw['changes']} Novas redes")
        
        if isinstance(sync_netw, dict) and sync_netw["changes"] > 0:
            logging.info(f"Reprocessando redes pendentes no banco de dados...")
            self.vuln.check_vuln_db()

        logging.info(f"Nenhuma rede nova..")
        

    def response(self, message, chat_id):
        link_requisicao = f'{self.url_base}sendMessage?chat_id={chat_id}&text={message}'
        requests.get(link_requisicao)