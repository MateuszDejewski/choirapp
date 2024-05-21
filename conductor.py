import keyring
class Conductor:
    def __init__(self,name:str,login:str,password:str) -> None:
        self.name=name
        self.login=login
        keyring.set_password("app",login,password)