from src.questionnaire import Questionnaire
import keyring

import abc

class User(metaclass=abc.ABCMeta):
    def __init__(self,name:str,login:str,password:str) -> None:
        self.name=name
        self.login=login
        keyring.set_password("app",login,password)
    
    def changelogin(self,newlogin:str)->None:
        oldlogin=self.login
        oldpassword=keyring.get_password("app",self.login)
        keyring.delete_password("app",oldlogin)
        keyring.set_password("app",newlogin,oldpassword)
        self.login=newlogin

    def changepassword(self,newpassword:str)->None:
        keyring.set_password("app",self.login,newpassword)

class Singer(User):
    def __init__(self,name:str,login:str,password:str,basicvoice:str) -> None:
        super().__init__(name,login,password)
        self.basicvoice=basicvoice
        self.answerdquestionnaires=[]
        self.questionnairesToAnswer=[]
        self.knownSongs=dict()
        self.unanswerdquestion=False

    def addQuestionnaire(self,quest:Questionnaire)->None:
        self.questionnairesToAnswer.append(quest)
        self.unanswerdquestion=True
    
    def answerQuestionniare(self,quest:Questionnaire,answers:list[str])->None:
        quest.addUserAnswer(self,answers)
        if quest.about and quest.multipleChoice==False:
            self.knownSongs[quest.about.song.name]=answers[0]
    
class Conductor(User):
    def __init__(self,name:str,login:str,password:str) -> None:
        super().__init__(name,login,password)