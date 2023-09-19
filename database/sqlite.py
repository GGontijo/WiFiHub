from interfaces.database_interface import DatabaseInterface
from contextlib import contextmanager
import sqlite3

class SQLite(DatabaseInterface):
    '''Classe de baixo nível'''

    def __init__(self, db_file):
        try:
            self.sqliteConnection = sqlite3.connect(db_file, check_same_thread=False)
            print(self.sqliteConnection)
            print(f"Successfully Connected to SQLite: {db_file}")

        except sqlite3.Error as error:
            print(f"Failed to connect to SQLite SQLite: {error}")

    @contextmanager
    def __cursor(self) -> None:
        cursor = self.sqliteConnection.cursor()
        try:
            yield (cursor)
        except Exception as e:
            cursor.close()
            raise e
        else:
            cursor.close()

    def close(self) -> None:
        if isinstance(self.sqliteConnection, sqlite3.Connection):
            self.sqliteConnection = self.sqliteConnection.close()
            print("The SQLite connection is closed")

        else:
            print('This object does not have a SQLite connection anymore!')

    def select(self, query: str) -> list:
        with self.__cursor() as cursor:
            cursor : sqlite3.Cursor
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows

    def delete(self, query: str) -> None:
        with self.__cursor() as cursor:
            cursor : sqlite3.Cursor
            response = cursor.execute(query)
            self.sqliteConnection.commit()
            print(response)

    def update(self, query: str) -> str:
        with self.__cursor() as cursor:
            cursor : sqlite3.Cursor
            response = cursor.execute(query)
            self.sqliteConnection.commit()
            return response

    def insert(self, query: str, nullaux= False) -> str:
        '''nullaux -> auxiliar parameter for NULL SQL keyword'''
        with self.__cursor() as cursor:
            cursor : sqlite3.Cursor
            if nullaux:
                response = cursor.execute(query, nullaux)
                self.sqliteConnection.commit()
                return response
            else:
                response = cursor.execute(query)
                self.sqliteConnection.commit()
                return response

#test = SQLite('unified_ap.sqlite')
#print(test.select('SELECT ssid, bssid FROM network_unified'))
