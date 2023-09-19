from typing import Type
from security.users import *
import secrets

pool_sessions = {}

class Session():
    '''Essa classe fica responsavel por criar e gerenciar
    as credenciais de sessões'''

    def __init__(self, _user) -> None:
        self.user = _user
        self.user: Type[Users]

    def start_session(self):
        self._id_user = self.user._login
        if self._id_user in pool_sessions:
            print("Usuário já possui sessão em andamento, reiniciando sessão...") ##log
            self.kill_session()
            self.start_session()
        self.token = secrets.token_hex(32)
        print(f"Sessão iniciada usuário: {self._id_user}, token: {self.token}") ##log
        pool_sessions[self._id_user] = self
        print('')
        return {'token': self.token}

    def kill_session(self):
        if self._id_user in pool_sessions:
            self.session = pool_sessions[self._id_user]
            if self.token != None:
                print(f"Sessão finalizada usuário: {self._id_user}") ##log
                del pool_sessions[self._id_user]
            else:
                print('Usuário não possui sessão em andamento!') ##log
                raise AttributeError('Usuário não possui sessão em andamento!')  
            return None #Throw error
            
