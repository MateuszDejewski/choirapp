from users import Singer,Conductor
from song import Song
from score import Score
from performance import Performance
from questionnaire import Questionnaire

class Choir:
    def __init__(self,name:str,conductors:list[Conductor]=[],singers:list[Singer]=[],songs:list[Song]=[],scores:list[Score]=[],performances:list[Performance]=[],questionnaires:list[Questionnaire]=[],tagsdict:dict[str:list[Song]]=dict()) -> None:
        self.name=name
        self.conductors=conductors
        self.singers=singers
        self.songs=songs
        self.scores=scores
        self.performances=performances
        self.qusetionnaires=questionnaires
        self.tagsdict=tagsdict

    def addSong(self,name:str,author:str="",description:str="",notes=None,recordings=None,startnotes:str="",tags:list[str]=[]):
        song=Song(name,author,self,description,notes,recordings,startnotes,tags)
        song.chceckAndDownloadFiles()
        self.songs.append(song)
    
    def addScore(self,song:Song,conductorcomments:str="",transposition:int=0,avaliable:bool=True,forUsers:list[Singer]=[]):
        score=Score(song,conductorcomments,transposition,avaliable,forUsers)
        self.scores.append(score)
    
    def getScoresForSinger(self,singer:Singer):
        scorelist=[]
        for score in self.scores:
            if score.avaliable or singer in score.forUsers:
                scorelist.append(score)
        return scorelist
    
    def getPerformancesForSinger(self,singer:Singer):
        perflist=[]
        for perf in self.performances:
            if singer in perf.singers:
                perflist.append(perf)
        return perflist
    
    def removeQuestionnaire(self,questionnaire:Questionnaire):
        self.qusetionnaires.remove(questionnaire)
        for singer in self.singers:
            singer.answerdquestionnaires.remove(questionnaire)
            singer.questionnairesToAnswer.remove(questionnaire)
    
    
        
