class Questionnaire:
    def __init__(self,question:str="",possibleAnswers:list[str]=[]) -> None:
        self.question=question
        self.possibleAnswers=possibleAnswers
        self.answers=dict()
    
    def addpossible_answer(self,answer:str):
        self.answers.append(answer)

    def adduseranswer(self,user,answer):
        self.answers[user]=answer
    
    def getresults(self):
        results={k:0 for k in self.possibleAnswers }
        for (k,v) in self.answers.items():
            results[v]+=1
        return results