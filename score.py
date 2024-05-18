
from questionnaire import Questionnaire
from song import Song
from music21 import interval
from pydub.playback import play

class Score:
    def __init__(self,song:Song,conductorcomments:str="",transposition:int=0) -> None:
        self.song=song
        self.questionare=Questionnaire("Czy znasz pieśń:"+self.song.name+"?",["Tak, czuje się w niej pewnie", "Tak, ale wymaga powtórzenia", "Jeszcze się jej uczę", "Na razie nie znam"])
        self.conductorcomments=conductorcomments
        self.transposition=transposition
        if transposition!=0:
            self.startsound=Score.transposeStartingNotes(self.song.startnotes,transposition)
        else:
            self.startsound=None

    def transposeStartingNotes(strNotes:str,change:int):
        """
        transpose starting notes by change number of semitons f.e. -2, -6
        """
        notes=Song.strnotesToRealnotes(strNotes)
        inter=interval.Interval(change)
        for nt in notes:
            nt.transpose(inter,inPlace=True)
        return Song.realnotesTosound(notes)
    
    def playrecording(self,name:str):
        self.song.playrecording(name)


    def playStartNotes(self):
        if self.startsound:
            oryginalsound=self.song.startsound
            self.song.startsound=self.startsound
            self.song.playStartNotes("startsoundT"+str(self.transposition)+".wav")
            self.song.startsound=oryginalsound
        else:
            self.song.playStartNotes()
