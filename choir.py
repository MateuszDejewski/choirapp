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
        success=song.chceckAndDownloadFiles()
        self.songs.append(song)
        return success
    
    def deleteSong(self,song:Song):
        try:
            song.deletefiles()
            song.setTags([])
            for score in self.scores:
                if score.song==song:
                    self.scores.remove(score)
            for perf in self.performances:
                for score in perf.songs:
                    if song==score.song:
                        perf.songs.remove(score)
            self.songs.remove(song)
        except ValueError:
            pass

    def deleteScore(self,score:Score):
        try:
            self.scores.remove(score)
            for perf in self.performances:
                    for sc in perf.songs:
                        if sc==score:
                            perf.songs.remove(score)
        except ValueError:
            pass
    
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
            if questionnaire in singer.answerdquestionnaires:
                singer.answerdquestionnaires.remove(questionnaire)
            if questionnaire in singer.questionnairesToAnswer:
                singer.questionnairesToAnswer.remove(questionnaire)
            
    
    
        
