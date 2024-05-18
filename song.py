from asyncio import sleep
import shutil as sh
from pathlib import Path
import os
import subprocess
import pytube as pt
import requests
import simpleaudio as sa
from music21 import note
import pydub
from pydub import AudioSegment
from pydub.generators import Sine
from pydub.playback import play
import pygame
pydub.AudioSegment.ffmpeg="C:/Users/mateu/ffmpeg-7.0-full_build/bin"


class Song:
    def __init__(self,name:str,author:str="",notes=None,recordings=None,startnotes:str="") -> None:
        self.name=name
        self.path="songs/"+name
        self.author=author
        if notes:
            self.notes=notes
        else:
            self.notes=dict()
        if recordings:
            self.recordings=recordings
        else:
            self.recordings=dict()
        self.startnotes=startnotes
        if startnotes!="":
            self.startsound=Song.createStartNotes(startnotes)
        else:
            self.startsound=None
        if not Path("songs").exists():
            os.mkdir("songs")
        if not Path(self.path).exists():
            oldpath=os.getcwd()
            os.chdir("songs")
            os.mkdir(self.path[6:])
            os.chdir(oldpath)
        pygame.mixer.init()

    def addFromPath(self,name:str,path:str)->str:
        oldname,ext= os.path.splitext(path)
        oldpath=os.getcwd()
        os.chdir(self.path)
        sh.copy(path,name+ext)
        os.chdir(oldpath)
        return ext
    
    def addFromGoogleDrive(self,name:str,url:str,ext:str)->None:
        file_id = url.split('/d/')[1].split('/view')[0]
        direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        data=requests.get(direct_link)
        oldpath=os.getcwd()
        os.chdir(self.path)
        with open(name+ext, 'wb')as file:
            file.write(data.content)
        os.chdir(oldpath)

    def addRecordingFromYoutube(self,name:str,url:str,ext:str="")->None:
            yt = pt.YouTube(url)
            video = yt.streams.filter(only_audio=True).desc().first()
            out_file = video.download(self.path)
            new_file = name + (ext if ext!="" else '.wav') 
            if Path(self.path+"/"+new_file).exists():
                os.remove(self.path+"/"+new_file)
            oldpath=os.getcwd()
            os.chdir(self.path)
            os.rename(out_file, new_file)
            os.chdir(oldpath)

            return ext if ext!="" else '.wav'

    def addnotes(self,resource:str,ext:str=""):
        name=self.name+str(len(self.notes)+1)
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
            self.notes.append((name+ext,resource))
        else:
            ext = self.addFromPath(name+ext,resource)
        self.notes[(name+ext)]=resource
    
    def addrecording(self,name:str,resource:str,ext:str=""):
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
        elif resource.startswith("https://www.youtube.com"):
            ext=self.addRecordingFromYoutube(name,resource,ext)
        else:
            ext = self.addFromPath(name+ext,resource)
        self.recordings[(name+ext)]=resource

    def playrecording(self,name:str):
        try:
            if self.recordings[name]:
                filepath=Path(self.path).joinpath(name)
                if not filepath.exists():
                    n,ext=os.path.splitext(name)
                    self.addrecording(n,self.recordings[name],ext)
                # wave_obj=sa.WaveObject.from_wave_file(filepath)
                # wave_obj.play()
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
        except:
            pass
    
    def playStartNotes(self,filename:str="startsound.wav"):
        filepath=Path(self.path).joinpath(filename)
        if not filepath.exists():
            oldpath=os.getcwd()
            os.chdir(self.path)
            self.startsound.export(filename,format='wav')
            os.chdir(oldpath)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        
        
    def strnotesToRealnotes(startnotes:str)->list[note.Note]:
        """
        Creates list of notes from string A4 F#4 Bb3 F2
        """
        singleNotes=startnotes.split(' ')
        notes=[]
        for elem in singleNotes:
            nt=note.Note(elem.replace("b","-"))
            notes.append(nt)
        return notes
    
    def realnotesTosound(notes:list[note.Note])->AudioSegment:
        """
        creates audiosegment with sound of notes
        """
        frequency=[]
        for nt in notes:
             frequency.append(nt.pitch.frequency)
        
        tone_duration = 1000  # in miliseconds = 1 second
        pause_duration = 500   

        audio = AudioSegment.silent(duration=0)
        for fr in frequency:
            tone = Sine(fr).to_audio_segment(duration=tone_duration)
            pause = AudioSegment.silent(duration=pause_duration)
            audio += tone + pause
        return audio

    def createStartNotes(startnotes:str)->AudioSegment:
        notes=Song.strnotesToRealnotes(startnotes)
        return Song.realnotesTosound(notes)  
