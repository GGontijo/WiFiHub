import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, send_from_directory
from helpers.db_helper import DbHelper
from services.telegram_importer import Telegram_Service
from vulns.vuln import Vuln
from web.map_helper import Map_Helper
from flask import jsonify
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')
_static_folder = os.path.join(os.getcwd(), 'web/static')

app = Flask(__name__, template_folder="web", static_folder=_static_folder)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
app.config['TEMPLATES_AUTO_RELOAD'] = True
db =  DbHelper()
vuln = Vuln(db)
telegram_service = Telegram_Service(db)

def start_api():
    app.run(host="0.0.0.0")
    
def start_server():
    api_thread = Thread(target=start_api)
    api_thread.start()
    telegram_service.process_messages()
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list')
def get_all_vulns():
    access_points = db.get_ap_all()
    ap_list = [ap.dict() for ap in access_points]
    return jsonify(ap_list)

@app.route('/updatemap')
def update_map():
    vuln.check_vuln_pending_db()
    return 'Processo de atualização do mapa finalizado.'

if __name__ == '__main__':
    start_server()