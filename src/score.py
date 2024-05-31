import os
from pathlib import Path
from src.questionnaire import Questionnaire
from src.song import Song
from src.users import Singer
from music21 import interval
from pydub import AudioSegment


class Score:
    def __init__(self,song:Song,conductorcomments:str="",transposition:int=0,avaliable:bool=True,forUsers:list[Singer]=[]) -> None:
        self.song=song
        self.questionnaire=Questionnaire("Czy znasz pieśń:"+self.song.name+"?",about=self,possibleAnswers=["Tak, czuje się w niej pewnie", "Tak, ale wymaga powtórzenia", "Jeszcze się jej uczę", "Na razie nie znam"])
        self.conductorcomments=conductorcomments
        self.transposition=0
        self.setTransposition(transposition)
        
        self.avaliable=avaliable
        self.forUsers=forUsers

    def setTransposition(self,transposition:int):
        oldpath= Path(self.song.path).joinpath("startsoundT"+str(self.transposition)+".wav")
        if oldpath.exists():
            os.remove(str(oldpath))

        self.transposition=transposition
        if transposition!=0:
            self.startsound=Score.transposeStartingNotes(self.song.startnotes,transposition)
        else:
            self.startsound=None
        
        if self.startsound:
            self.song.exportStartsound(self.startsound,"startsoundT"+str(self.transposition)+".wav")

    def transposeStartingNotes(strNotes:str,change:int)->AudioSegment|None:
        """
        transpose starting notes by change number of semitons f.e. -2, -6
        """
        if not strNotes or strNotes=="":
            return None
        
        notes=Song.strnotesToRealnotes(strNotes)
        inter=interval.Interval(change)
        for nt in notes:
            nt.transpose(inter,inPlace=True)
        return Song.realnotesTosound(notes)
    
    def playrecording(self,name:str)->None:
        self.song.playrecording(name)

    def playStartNotes(self)->None:
        if self.startsound:
            self.song.playStartNotes("startsoundT"+str(self.transposition)+".wav")
        else:
            self.song.playStartNotes()

    def shareToSinger(self,singer:Singer)->None:
        self.forUsers.append(singer)
    
    # def __eq__(self, value: object) -> bool:
    #     if isinstance(value,Score):
    #         return self.song.__eq__(value.song)
    #     return False
