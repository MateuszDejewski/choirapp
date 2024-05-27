from questionnaire import Questionnaire
from song import Song
from users import Singer
from music21 import interval
from pydub import AudioSegment


class Score:
    def __init__(self,song:Song,conductorcomments:str="",transposition:int=0,avaliable:bool=True,forUsers:list[Singer]=[]) -> None:
        self.song=song
        self.questionnaire=Questionnaire("Czy znasz pieśń:"+self.song.name+"?",about=self,possibleAnswers=["Tak, czuje się w niej pewnie", "Tak, ale wymaga powtórzenia", "Jeszcze się jej uczę", "Na razie nie znam"])
        self.conductorcomments=conductorcomments
        self.transposition=transposition
        if transposition!=0:
            self.startsound=Score.transposeStartingNotes(self.song.startnotes,transposition)
        else:
            self.startsound=None

        self.avaliable=avaliable
        self.forUsers=forUsers
        

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
            oryginalsound=self.song.startsound
            self.song.startsound=self.startsound
            self.song.playStartNotes("startsoundT"+str(self.transposition)+".wav")
            self.song.startsound=oryginalsound
        else:
            self.song.playStartNotes()

    def shareToSinger(self,singer:Singer)->None:
        self.forUsers.append(singer)
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value,Score):
            return self.song.__eq__(value.song)
        return False
