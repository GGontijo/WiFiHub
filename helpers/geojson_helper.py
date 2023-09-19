from helpers.db_helper import DbHelper
import json

class GeoJsonHelper:

    def __init__(self, db: DbHelper) -> None:
        self.db = db
        self.ap_list = self.db.get_ap_all()

    def generate(self):

        geojson = {}
        geojson['type'] = 'FeatureCollection'
        features = []
    
        for ap in self.ap_list:
            feature = {}
            properties = {}
            geometry = {}
            coordinates = []
            coordinates.append(ap['bestlon'])
            coordinates.append(ap['bestlat'])
            geometry['type'] = 'Point'
            geometry['coordinates'] = coordinates
            properties['ssid'] = ap['ssid']
            properties['mac'] = ap['mac']
            properties['type'] = ap['type']
            properties['capabilities'] = ap['capabilities']
            properties['password'] = ap['password']
            if properties['password'] == None:
                properties['marker-color'] = "#00ffe1"
                properties['marker-size'] = "small"
                properties['marker-symbol'] = "circle-stroked"
            else:
                properties['marker-color'] = "#ff0000"
                properties['marker-size'] = "medium"
                properties['marker-symbol'] = "minefield"
            feature['type'] = 'Feature'
            feature['properties'] = properties
            feature['geometry'] = geometry
            features.append(feature)
            geojson['features'] = features
            #geojson_object = json.dumps(geojson, indent= 4)
        
        with open('data.json', 'w') as f:
            json.dump(geojson, f)