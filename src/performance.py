import pendulum
from src.score import Score
from src.users import Singer

class Performance:
    def __init__(self,name:str,date:pendulum=None,details:str="",songs:list[Score]=[],conductor=None,singers:list[Singer]=[]) -> None:
        self.name=name
        self.date=date
        self.details=details
        self.songs=songs
        self.conductor=conductor
        self.singers=singers
        for score in songs:
            for singer in singers:
                score.shareToSinger(singer)
    
    def addSong(self,song:Score,index:int=None)->None:
        if index:
            self.songs.insert(index,song)
        else:
            self.songs.append(index)
    
    def addSinger(self,singer:Singer)->None:
        if not singer in self.singers:
            self.singers.append(singer)
    
    def removeSong(self,song:Score)->None:
        if song in self.songs:
            self.songs.remove(song)
    
    def removeSinger(self,singer:Singer)->None:
        if singer in self.singers:
            self.singers.remove(singer)
    
    
