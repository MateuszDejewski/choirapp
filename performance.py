import pendulum
from score import Score
from singer import Singer
from song import Song

class Performance:
    def __init__(self,name:str,date:pendulum=None,details:str="",songs:list[Score]=[],conductor=None,singers=[]) -> None:
        self.name=name
        self.date=date
        self.details=details
        self.songs=songs
        self.conductor=conductor
        self.singers=singers
    
    def addSong(self,song:Score,index:int=None):
        if index:
            self.songs.insert(index,song)
        else:
            self.songs.append(index)
    
    def addSinger(self,singer:Singer):
        if not singer in self.singers:
            self.singers.append(singer)
    

