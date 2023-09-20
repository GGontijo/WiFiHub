import os
import folium
from folium.plugins import MarkerCluster
from helpers.db_helper import DbHelper

class map_helper:
    '''To refer's: https://python-visualization.github.io/folium/plugins.html
    https://github.com/Leaflet/Leaflet.markercluster#customising-the-clustered-markers
    https://nbviewer.org/urls/hugedot.pl/projekt_studia/projekt/wizualizacja/mapa.ipynb'''
    def __init__(self, db: DbHelper) -> None:
        _start_coord = [-15.595485,-56.092638]
        self._map = folium.Map(location=_start_coord, zoom_start=14)
        self.file = os.path.join('web', 'index.html')
        self.db = db
        self.ap_geodata = self.db.get_ap_all()
        #self.generate_heavy_pwned()
        self.generate_heavy_all()
        
    def generate_heavy_all(self):
        coordinates = []
        for ap in self.ap_geodata:
            subcoordinates = [ap.bestlat, ap.bestlon]
            coordinates.append(subcoordinates)
        self._map.add_child(MarkerCluster(coordinates))
        return self.render()

    def generate_heavy_pwned(self):
        for ap in self.ap_geodata:
            if ap.password != None:
                subcoordinates = [ap.bestlat, ap.bestlon]
                popup_info = {"SSID": ap.ssid, 
                            "MAC": ap.bssid, 
                            "Password": ap.password}
                folium.Marker(location=[subcoordinates[0], subcoordinates[1]], popup=popup_info).add_to(self._map)
        return self.render()

    def generate_opt_all(self):
        unpwned_coordinates = []
        pwned_coordinates = []
        for ap in self.ap_geodata:
            if ap.password == None:
                subcoordinates = [ap.bestlat, ap.bestlon]
                unpwned_coordinates.append(subcoordinates)
            else:
                subcoordinates= [ap.bestlat, ap.bestlon]
                pwned_coordinates.append(subcoordinates)
        unpwned_layer = folium.FeatureGroup(name='unpwned')
        pwned_layer = folium.FeatureGroup(name='pwned')
        unpwned_cluster = MarkerCluster(options={'maxClusterRadius': 100}).add_to(unpwned_layer)
        pwned_cluster = MarkerCluster(options={'maxClusterRadius': 1}).add_to(pwned_layer)
        for coord in unpwned_coordinates:    
            folium.Marker(coord).add_to(unpwned_cluster)
        for coord in pwned_coordinates:
            folium.Marker(coord).add_to(pwned_cluster)
        self._map.add_child(unpwned_layer)
        self._map.add_child(pwned_layer)
        self._map.add_child(folium.LayerControl())
        return self.render()

    def generate_opt_pwned(self): ##todo
        unpwned_coordinates = []
        pwned_coordinates = []
        for ap in self.ap_geodata:
            if ap['password'] == None:
                subcoordinates = [ap.bestlat, ap.bestlon]
                unpwned_coordinates.append(subcoordinates)
            else:
                subcoordinates= [ap.bestlat, ap.bestlon]
                pwned_coordinates.append(subcoordinates)
        unpwned_layer = folium.FeatureGroup(name='unpwned')
        pwned_layer = folium.FeatureGroup(name='pwned')
        unpwned_cluster = MarkerCluster(options={'maxClusterRadius': 100}).add_to(unpwned_layer)
        pwned_cluster = MarkerCluster(options={'maxClusterRadius': 1}).add_to(pwned_layer)
        for coord in unpwned_coordinates:    
            folium.Marker(coord).add_to(unpwned_cluster)
        for coord in pwned_coordinates:
            folium.Marker(coord).add_to(pwned_cluster)
        self._map.add_child(unpwned_layer)
        self._map.add_child(pwned_layer)
        self._map.add_child(folium.LayerControl())
        return self.render()

    def render(self):
        return self._map.save(self.file)