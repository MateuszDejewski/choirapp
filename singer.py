
from questionnaire import Questionnaire
import keyring

class Singer:
    def __init__(self,name:str,login:str,password:str,basicvoice:str) -> None:
        self.name=name
        self.login=login
        keyring.set_password("app",login,password)
        self.basicvoice=basicvoice
        self.answerdquestionnaires=[]
        self.questionnairesToAnswer=[]
        self.knownSongs=dict()
        self.unanswerdquestion=False

    def addQuestionnaire(self,quest:Questionnaire):
        self.questionnairesToAnswer.append(quest)
        self.unanswerdquestion=False
    
    def answerQuestionniare(self,quest:Questionnaire,answers:list[str]):
        quest.adduseranswer(self,answers)
        if quest.about and quest.multipleChoice==False:
            self.knownSongs[quest.about.song.name]=answers[0]

    
    
    