from users import Singer,Conductor
from song import Song
from score import Score
from performance import Performance
from questionnaire import Questionnaire

class Choir:
    def __init__(self,name:str,conductors:list[Conductor]=[],singers:list[Singer]=[],songs:list[Song]=[],scores:list[Score]=[],performances:list[Performance]=[],questionnaires:list[Questionnaire]=[]) -> None:
        self.name=name
        self.conductors=conductors
        self.singers=singers
        self.songs=songs
        self.scores=scores
        self.performaces=performances
        self.qusetionnaires=questionnaires

    def addSong(self,name:str,author:str="",description:str="",notes=None,recordings=None,startnotes:str=""):
        song=Song(name,author,self,description,notes,recordings,startnotes)
        song.chceckAndDownloadFiles()
        self.songs.append(song)
    
    def addScore(self,song:Song,conductorcomments:str="",transposition:int=0,avaliable:bool=True,forUsers:dict[Singer:str]=dict()):
        score=Score(song,conductorcomments,transposition,avaliable,forUsers)
        self.scores.append(score)

    def getSocoresForSinger(self,singer:Singer):
        scorelist=[]
        for score in self.scores:
            if score.avaliable or singer in score.forUsers:
                scorelist.append(score)
    
    def getPerformancesForSinger(self,singer:Singer):
        perflist=[]
        for perf in self.performaces:
            if singer in perf.singers:
                perflist.append(perf)
    
    def removeQuestionnaire(self,questionnaire:Questionnaire):
        self.qusetionnaires.remove(questionnaire)
        for singer in self.singers:
            singer.answerdquestionnaires.remove(questionnaire)
            singer.unanswerdquestion.remove(questionnaire)
    
    
        
