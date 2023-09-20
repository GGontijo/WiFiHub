from abc import ABC, abstractmethod

class DatabaseInterface(ABC):

    @abstractmethod
    def select(self, database):
        pass

    @abstractmethod
    def update(self, database):
        pass

    @abstractmethod
    def delete(self, database):
        pass