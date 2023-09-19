from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    '''Interface de alto nível que faz a integração com o banco de dados SQLite'''

    @abstractmethod
    def select(self, database):
        pass

    @abstractmethod
    def update(self, database):
        pass

    @abstractmethod
    def delete(self, database):
        pass