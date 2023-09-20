from ast import List
from typing import List
from database.sqlite import SQLite
from models.base_models import AccessPoint, NewAccessPoint

class DbHelper:

    def __init__(self) -> None:
        self.db_file = 'database/unified_ap.sqlite'
        self.dbconn = SQLite(self.db_file)

    def get_ap_mac(self) -> list:       
        list = []
        query = "SELECT ssid, bssid FROM network;"
        rows = self.dbconn.select(query)
        for item in rows:
            ap = NewAccessPoint(ssid=item[0],
                             mac=item[1])
            list.append(ap)
        return list

    def update_ap_passwd(self, ap: NewAccessPoint) -> None:
        '''Atualiza a senha de um determinado access point já existente na tabela'''
        if isinstance(ap, List):
            for ap in ap:
                q = f"UPDATE network SET password = '{ap.password}' WHERE bssid = '{ap.mac}';"
                response = self.dbconn.update(q)
        
        return response.connection.total_changes

    def sync_network(self, db_e) -> dict:
        '''Método que sincroniza a tabela network a partir de um banco recebido (db_e) ao
        banco interno (db_i)'''
        db_i = self.dbconn
        db_e = SQLite(db_e)
        
        #Insere redes que não existiam
        query_netw_a = "select bssid from network"
        rows = db_i.select(query_netw_a)
        bssid_list = []
        for row in rows:
            bssid_list.append(row[0])

        query_netw_b = f"select * from network where network.bssid not in ({str(bssid_list)[1:-1]})" #"insert into network select *, NULL from network where network.bssid not in ({rows})"
        rows = db_e.select(query_netw_b)
        db_e.close()
        if not rows:
            return {"status": "PASS", "changes": 0}

        ap_list = []
        for item in rows:
            ap_sub_list = []
            ap_sub_list.append(item[0])
            ap_sub_list.append(item[1])
            ap_sub_list.append(item[2])
            ap_sub_list.append(item[3])
            ap_sub_list.append(item[4])
            ap_sub_list.append(item[5])
            ap_sub_list.append(item[6])
            ap_sub_list.append(item[7])
            ap_sub_list.append(item[8])
            ap_sub_list.append(item[9])
            ap_sub_list.append(item[10])
            ap_list.append(ap_sub_list)

        for ap in ap_list:
            response = db_i.insert(f'insert into network values({str(ap)[1:-1]}, ?)', (None, ))

        return {"status": "OK", "changes": response.connection.total_changes}

    def sync_location(self, db_e) -> bool:
        '''Método que sincroniza a tabela location a partir de um banco recebido (db_e) ao
        banco interno (db_i)'''
        db_i = self.dbconn
        db_e = SQLite(db_e)

        #Insere localizações cujo time não existia
        query_loc_a = "select time from location group by time"
        rows = db_i.select(query_loc_a)
        loc_list = []
        for row in rows:
            loc_list.append(row[0])
        query_loc_b = f"select bssid, level, lat, lon, altitude, accuracy, time, external from location where location.time not in ({str(loc_list)[1:-1]})" #"insert into location select NULL, bssid, level, lat, lon, altitude, accuracy, time, external from location where location.time not in ({rows})"
        rows = db_e.select(query_loc_b) #debug
        db_e.close()
        if not rows:
            return {"status": "PASS", "changes": 0}

        ap_list = []
        for item in rows:
            ap_sub_list = []
            ap_sub_list.append(item[0])
            ap_sub_list.append(item[1])
            ap_sub_list.append(item[2])
            ap_sub_list.append(item[3])
            ap_sub_list.append(item[4])
            ap_sub_list.append(item[5])
            ap_sub_list.append(item[6])
            ap_sub_list.append(item[7])
            ap_list.append(ap_sub_list)
        
        for ap in ap_list:
            response = db_i.insert(f'insert into location values(?,{str(ap)[1:-1]})', (None,))

        return {"status": "OK", "changes": response.connection.total_changes}

    def sync_route(self, db_e) -> bool:
        '''Método que sincroniza a tabela route a partir de um banco recebido (db_e) ao
        banco interno (db_i)'''
        db_i = self.dbconn
        db_e = SQLite(db_e)

        #Insere rotas cujo time não existia
        query_route_a = "select time from route group by time"
        rows = db_i.select(query_route_a)
        route_list = []
        for row in rows:
            route_list.append(row[0])
        query_route_b = f"select run_id, wifi_visible, cell_visible, bt_visible, lat, lon, altitude, accuracy, time from route where route.time not in ({str(route_list)[1:-1]})" #"insert into route select NULL, run_id, wifi_visible, cell_visible, bt_visible, lat, lon, altitude, accuracy, time from route where route.time not in ({rows})"
        rows = db_e.select(query_route_b) #debug
        db_e.close()
        if not rows:
            return {"status": "PASS", "changes": 0}

        ap_list = []
        for item in rows:
            ap_sub_list = []
            ap_sub_list.append(item[0])
            ap_sub_list.append(item[1])
            ap_sub_list.append(item[2])
            ap_sub_list.append(item[3])
            ap_sub_list.append(item[4])
            ap_sub_list.append(item[5])
            ap_sub_list.append(item[6])
            ap_sub_list.append(item[7])
            ap_sub_list.append(item[8])
            ap_list.append(ap_sub_list)
        
        for ap in ap_list:
            response = db_i.insert(f'insert into route values(?,{str(ap)[1:-1]})', (None,))

        return {"status": "OK", "changes": response.connection.total_changes}

    def get_ap_all(self) -> List[AccessPoint]:
        query = "SELECT * FROM network;"
        ap_list = []
        rows = self.dbconn.select(query)
        for item in rows:
            ap = AccessPoint(
            bssid=item[0],
            ssid=item[1],
            frequency=item[2],
            capabilities=item[3],
            lasttime=item[4],
            lastlat=item[5],
            lastlon=item[6],
            type=item[7],
            bestlevel=item[8],
            bestlat=item[9],
            bestlon=item[10],
            password=item[11],
            )
            ap_list.append(ap)
        return ap_list