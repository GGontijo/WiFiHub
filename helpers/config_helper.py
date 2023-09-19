import json

class Config:
    '''Singleton approach'''

    _instance = None

    def __init__(self) -> None:
        CONFIG_FILE = 'config.json'
        with open(CONFIG_FILE, 'r') as config:
            self.__config = json.load(config)
        
    def get_config(self, var: str) -> str:
        value = self.__config[var]
        return value

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance