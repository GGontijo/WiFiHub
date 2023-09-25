import logging
import os
import folium
from folium.features import CustomIcon
from folium.plugins import MarkerCluster
from helpers.db_helper import DbHelper

class Map_Helper:
    '''To refer's: https://python-visualization.github.io/folium/plugins.html
    https://github.com/Leaflet/Leaflet.markercluster#customising-the-clustered-markers
    https://nbviewer.org/urls/hugedot.pl/projekt_studia/projekt/wizualizacja/mapa.ipynb'''
    def __init__(self, db: DbHelper) -> None:
        self._start_coord = [-15.595485,-56.092638]
        self.file = os.path.join('web', 'index.html')
        self.db = db
        self.vulnerable_icon = CustomIcon(
            icon_image=os.path.join('web', 'icons', '001-wifi.png'),
            icon_size=(32, 32),
        )
        #self.generate_heavy_pwned()
        #self.generate_heavy_all()
        #self.generate_opt_pwned()
        
    def generate_heavy_all(self):
        '''Gera o mapa com as redez não vulneráveis, sem utilizar cluster'''
        self.ap_geodata = self.db.get_ap_all()
        self._map = folium.Map(location=self._start_coord, zoom_start=25)
        cluster = MarkerCluster()
        for ap in self.ap_geodata:
            if ap.password == None:
                coord = [ap.bestlat, ap.bestlon]
                folium.Marker(coord, icon=self.non_vulnerable_icon).add_to(cluster)
            else:
                coord = [ap.bestlat, ap.bestlon]
                _icon = CustomIcon(
                    icon_image=os.path.join('web', 'icons', '001-wifi.png'),
                    icon_size=(32, 32))
                folium.Marker(coord, icon=_icon).add_to(cluster)
        self._map.add_child(cluster)
        return self.render()

    def generate_heavy_pwned(self):
        '''Gera o mapa com as redez vulneráveis, sem utilizar cluster'''
        self.ap_geodata = self.db.get_ap_all()
        self._map = folium.Map(location=self._start_coord, zoom_start=25)
        for ap in self.ap_geodata:
            if ap.password is not None:
                popup_info = f"SSID: {ap.ssid}<br>MAC: {ap.bssid}<br>Password: {ap.password}"
                _icon = CustomIcon(
                    icon_image=os.path.join('web', 'icons', '001-wifi.png'),
                    icon_size=(32, 32))
                folium.Marker(location=[ap.bestlat, ap.bestlon], popup=popup_info, icon=_icon).add_to(self._map)

    def generate_opt_all(self):
        '''Gera o mapa com apenas redes vulneráveis e não vulneráveis, com níveis distintos de clusterização entre elas'''
        self.ap_geodata = self.db.get_ap_all()
        self._map = folium.Map(location=self._start_coord, zoom_start=25)
        unpwned_layer = folium.FeatureGroup(name='unpwned')
        pwned_layer = folium.FeatureGroup(name='pwned')
        unpwned_cluster = MarkerCluster(options={'maxClusterRadius': 100}).add_to(unpwned_layer)
        pwned_cluster = MarkerCluster(options={'maxClusterRadius': 20}).add_to(pwned_layer)
        for ap in self.ap_geodata:
            if ap.password == None:
                coord = [ap.bestlat, ap.bestlon]
                _icon = CustomIcon(
                    icon_image=os.path.join('web', 'icons', '002-wifi-1.png'),
                    icon_size=(32, 32),
                )
                folium.Marker(coord, icon=_icon).add_to(unpwned_cluster)
            else:
                coord = [ap.bestlat, ap.bestlon]
                popup_info = f"SSID: {ap.ssid}<br>MAC: {ap.bssid}<br>Password: {ap.password}"
                _icon = CustomIcon(
                    icon_image=os.path.join('web', 'icons', '001-wifi.png'),
                    icon_size=(32, 32))
                folium.Marker(coord, popup=popup_info, icon=_icon).add_to(pwned_cluster)
        self._map.add_child(unpwned_layer)
        self._map.add_child(pwned_layer)
        self._map.add_child(folium.LayerControl())

    def generate_opt_pwned(self):
        '''Gera o mapa com apenas as redes vulneráveis e compiladas'''
        self.ap_geodata = self.db.get_ap_all()
        self._map = folium.Map(location=self._start_coord, zoom_start=25)
        pwned_layer = folium.FeatureGroup(name='pwned')
        pwned_cluster = MarkerCluster(options={'maxClusterRadius': 25}).add_to(pwned_layer)
        for ap in self.ap_geodata:
            if ap.password is not None:
                coord = [ap.bestlat, ap.bestlon]
                popup_info = f"SSID: {ap.ssid}<br>MAC: {ap.bssid}<br>Password: {ap.password}"
                _icon = CustomIcon(
                    icon_image=os.path.join('web', 'icons', '001-wifi.png'),
                    icon_size=(32, 32))
                folium.Marker(coord, popup=popup_info, icon=_icon).add_to(pwned_cluster)
        self._map.add_child(pwned_layer)
        self._map.add_child(folium.LayerControl())

    def render(self, type: str = None):
        # TODO: Filtrar pelo type para gerar heavy all, heavy pwned, opt all ou opt pwned...
        #if type:
        #    Filtrar...
        #    Retorno.
        self.generate_opt_pwned()
        self._map.save(self.file)
        logging.info('Mapa atualizado!')