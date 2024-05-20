

from conductor import Conductor
from singer import Singer
from song import Song
from score import Score
from performance import Performance

class Choir:
    def __init__(self,name:str,conductors:list[Conductor]=[],singers:list[Singer]=[],songs:list[Song]=[],scores:list[Score]=[],performances:list[Performance]=[]) -> None:
        self.name=name
        self.conductors=conductors
        self.singers=singers
        self.songs=songs
        self.scores=scores
        self.performaces=performances

    def addSong(self,name:str,author:str="",description:str="",notes=None,recordings=None,startnotes:str=""):
        song=Song(name,author,description,notes,recordings,startnotes)
        song.chceckAndDownloadFiles()
        self.songs.append(song)

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
                
        
    
        
