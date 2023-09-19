from helpers.geojson_helper import GeoJsonHelper
from helpers.map_helper import map_helper
from helpers.db_helper import DbHelper
from services.telegram_importer import Telegram_Service
from vulns.vuln import Vuln

class Core:

    def __init__(self) -> None:
        self.db =  DbHelper()
        #self.telegram_service = Telegram_Service(self.db)
        self.vuln = Vuln(self.db)
        #self.geojson = GeoJsonHelper(self.db)
        self.map = map_helper(self.db)
        
    def exec(self):
        pass
        #self.vuln.check_vuln_db()
        #self.vuln.get_pwned_passw()
        #self.geojson.generate()
        #self.telegram_service.process_messages()
        

    def audit(self, ssid):
        return self.vuln.check(ssid)
    
    def compile(self, ssid, mac):
        return self.vuln.compile(ssid, mac)


if __name__ == '__main__':
    core = Core()
    core.exec()