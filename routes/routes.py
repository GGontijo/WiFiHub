from fastapi import APIRouter
from security.users import *
from core import Core
from security.authentication import Auth
from pydantic import BaseModel

class Usuario(BaseModel):
    login: str
    password: str

class Session(BaseModel):
    token: str

router = APIRouter()

#core_app = Core()

@router.get("/get_all_vulns")
def get_all_vulns():
    pass

#@router.get("/check/{ssid}")
#def check(ssid):
#    return core_app.audit(ssid)
#
#@router.get("/compile/{ssid}")
#def compile(ssid, mac: str):
#    return core_app.compile(ssid, mac)

@router.get("/login/{login}")
def login(login: str, password: str):
    return Auth(login, password)
    
@router.post("/session/token")
def token(usuario: Usuario):
    _login = usuario.login
    _password = usuario.password
    return Auth.authenticate_user(_login, _password)

@router.post("/security/create_user")
def create_user(usuario: Usuario):
    _login = usuario.login
    _password = usuario.password
    return Users.create_user(_login, _password)