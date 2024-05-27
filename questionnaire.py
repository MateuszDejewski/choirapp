class Questionnaire:
    def __init__(self,question:str="",about=None,possibleAnswers:list[str]=[],addingNewAnswers:bool=False,multipleChoice:bool=False) -> None:
        self.question=question
        self.about=about
        self.answers=dict()
        self.possibleAnswers=[]
        for ans in possibleAnswers:
            self.addPossibleAnswer(ans)
        self.addingNewAnswers=addingNewAnswers
        self.multipleChoice=multipleChoice
           
    def addPossibleAnswer(self,answer:str)->None:
        self.possibleAnswers.append(answer)
        self.answers[answer]=[]

    def addUserAnswer(self,user,answer:list[str]|str)->bool:
        for k,v in list(self.answers.items()):
            if user in v:
                v.remove(user)
        
        if isinstance(answer,str):
            if not answer in self.possibleAnswers:
                if self.addingNewAnswers:
                    self.possibleAnswers.append(answer)
                else:
                    return False
            self.answers[answer].append(user)
            return True
        elif self.multipleChoice:
            for ans in answer:
                if ans in self.possibleAnswers:
                    self.answers[ans].append(user)
                elif self.addingNewAnswers:
                    self.possibleAnswers.append(ans)
                    self.answers[ans].append(user)
            return True
        else:
            for ans in answer:
                if ans in self.possibleAnswers:
                    self.answers[ans].append(user)
                    return True
    
    def getResults(self)->dict['User':int]:
        results={k:0 for k in self.possibleAnswers }
        for (k,v) in self.answers.items():
            results[k]=len(v)
        return results
    
    def __eq__(self,other:object)->bool:
        if isinstance(other,Questionnaire):
            return self.question==other.question
        return False