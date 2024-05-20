
from questionnaire import Questionnaire


class Singer:
    def __init__(self,name:str,basicvoice:str) -> None:
        self.name=name
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

    
    
    