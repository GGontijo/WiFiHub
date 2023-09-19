from security.users import *


class Auth():

    def authenticate_user(login: str, password: str):
        return Users.login(login, password)

    def desauthenticate_user(user):
        Users.logout(user)
        

Users.create_user('gabriel', '123')

#userobj = Auth.authenticate_user('gabriel', '123')
#userobj.block_user()
#userobj.logout()
#userobj.unblock_user()
#
#userobj2 = Auth.authenticate_user('gabriel', '123')
#print('')

