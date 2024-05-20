class Questionnaire:
    def __init__(self,question:str="",about=None,possibleAnswers:list[str]=[],addingNewAnswers:bool=False,multipleChoice:bool=False) -> None:
        self.question=question
        self.about=about
        self.possibleAnswers=possibleAnswers
        self.addingNewAnswers=addingNewAnswers
        self.multipleChoice=multipleChoice
        self.answers=dict()
    
    def addPossibleAnswer(self,answer:str):
        self.answers.append(answer)

    def addUserAnswer(self,user,answer:list[str]|str)->bool:
        if isinstance(answer,str):
            if not answer in self.possibleAnswers:
                if self.addingNewAnswers:
                    self.possibleAnswers.append(answer)
                else:
                    return False
            self.answers[user]=[answer]
            return True
        elif self.multipleChoice:
            acceptable=[]
            for ans in answer:
                if ans in self.possibleAnswers:
                    acceptable.append(ans)
                elif self.addingNewAnswers:
                    self.possibleAnswers.append(ans)
                    acceptable.append(ans)
            self.answers[user]=acceptable
            return True
        else:
            for ans in answer:
                if ans in self.possibleAnswers:
                    self.answers[user]=[ans]
                    return True
    
    def getResults(self):
        results={k:0 for k in self.possibleAnswers }
        for (k,v) in self.answers.items():
            for ans in v:
                results[ans]+=1
        return results