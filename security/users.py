import hashlib
from security import sessions
from typing import Type

all_users = {}

class Users():

    def __init__(self, login: str= None, password: str= None) -> None:
        '''aqui foi feito um tratamento de exceptions por conta do init não poder retornar nada..
        mas o ideal é que todo o código passe a lidar com exceções em erros e não returns.
        if a parameter is passed, we assume that is needed to create an user.'''
        try:
            if login and password:
                if login not in all_users: #We check if all_users is initiated and confirm that there's no an alredy created user.
                    self._login = login
                    self._password = hashlib.sha256(password.encode(encoding = 'UTF-8')).hexdigest()
                    self.status = None
                    self.blocked = False
                    all_users[login] = self #Guarda um objeto do usuário na variavel global
                else:
                    self.error = 'Esse usuário já existe!'
                    raise AttributeError(self.error)
            else:
                #get users from DB and store it's objects in users {}
                pass
        except Exception as e:
            print(e) #log


    def create_user(login: str, password: str):
        return Users(login, password)
        
    def block_user(self):
            self.blocked = True
            self.session.kill_session() #Mata qualquer sessão em andamento.
            print(f"Usuário {self._login} bloqueado!") ##log
            return f"Usuário {self._login} bloqueado!"

    def unblock_user(self):
        self.blocked = False
        print(f"Usuário {self._login} desbloqueado!") ##log
        return f"Usuário {self._login} desbloqueado!"

    def login(login: str, password: str):
        if login not in all_users:
            return 'Login ou senha incorretos!'
        _user = all_users[login]
        _user: Type[Users] #typing hint
        if hashlib.sha256(password.encode(encoding = 'UTF-8')).hexdigest() != _user._password:
            return 'Login ou senha incorretos!'
        else:
            return _user.change_status(1)

    def logout(self):
        return self.change_status(0)


    def change_status(self, status: int):
        match status:
            case 0: #Fechar sessão
                self.status = status
                self.session.kill_session()
                return {'message': 'Usuário Desautenticado!'}

            case 1: #Abrir sessão
                if self.blocked == True:
                    raise AttributeError('Usuário está bloqueado! Favor verificar')
                if self._login in sessions.pool_sessions:
                    self.session = sessions.pool_sessions[self._login]
                else: 
                    self.session = sessions.Session(self) #abre a sessão
                self.status = status
                self.session.start_session()
                return {'message': 'Usuário Autenticado!', 'token': self.session.token}
