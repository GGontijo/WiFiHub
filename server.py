import logging
from flask import Flask, render_template
from helpers.db_helper import DbHelper
from services.telegram_importer import Telegram_Service
from vulns.vuln import Vuln
from web.map_helper import map_helper
from flask import jsonify
from threading import Thread

app = Flask(__name__, template_folder="web")

db =  DbHelper()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

class Server:
    def __init__(self) -> None:
        self.telegram_service = Telegram_Service(db)
        self.vuln = Vuln(db)
        self.map = map_helper(db)

    def start_api(self):
        app.run()

    def start(self):
        api_thread = Thread(target=self.start_api)
        api_thread.start()
        self.telegram_service.process_messages()
    

    @app.route('/')
    def index():
        return render_template('index.html')
    
    
    @app.route('/compile')
    def compile():
        return 'Lá ele!'
        #ssid = request.args.get('ssid')
        #mac = request.args.get('mac')
        #if ssid and mac:
        #    logging.info(f"Compilando para o SSID: {ssid}, MAC: {mac}")
        #    return 
        #else:
        #    return "Parâmetros 'ssid' e 'mac' não fornecidos corretamente na URL."


    @app.route('/list')
    def get_all_vulns():
        access_points = db.get_ap_all()
        ap_list = [ap.dict() for ap in access_points]
        return jsonify(ap_list)

if __name__ == '__main__':
    s = Server()
    s.start()