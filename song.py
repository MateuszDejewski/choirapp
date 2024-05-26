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
import pygame
from moviepy.editor import *
pygame.mixer.init()



class Song:
    def __init__(self,name:str,author:str,choir,description:str="",notes=None,recordings=None,startnotes:str="") -> None:
        self.name=name
        self.path = os.path.join("songs",choir.name,name)
        self.author=author
        self.description=description
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
        
        olddir=os.getcwd()
        if not Path("songs").exists():
            os.mkdir("songs")
        os.chdir("songs")
        if not Path(choir.name).exists():
            os.mkdir(choir.name)
        os.chdir(choir.name)
        if not Path(name).exists():
            os.mkdir(name)
        
        os.chdir(olddir)
        self.playobj=None

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

    def addRecordingFromYoutube(self,file:str,url:str)->None:
            olddir=os.getcwd()
            os.chdir(self.path)

            yt = pt.YouTube(url)
            stream = yt.streams.filter(only_audio=True,file_extension='mp4').first()
            download_path = stream.download(filename="audio.mp4")

            Song.convertToMP3("audio.mp4",file,"mp4")
            os.remove("audio.mp4")
            os.chdir(olddir)
            return ".mp3"
            

    def addnotes(self,resource:str,name:str="",ext:str=""):
        if name=="":
            name=self.name+str(len(self.notes)+1)
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
        else:
            ext = self.addFromPath(name,resource)
        self.notes[(name+ext)]=resource
    
    def convertToMP3(inputpath:str,outputpath:str,ext:str):
        try:
            audio=AudioSegment.from_file(inputpath,format=ext)
            audio.export(outputpath,format='mp3')
        except Exception:
            raise RuntimeError("Unable to conver file")


    def addrecording(self,name:str,resource:str,ext:str=""):
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
        elif resource.startswith("https://www.youtube.com") or resource.startswith("https://youtu.be"):
            ext=self.addRecordingFromYoutube(name+".mp3",resource)
        else:
            ext = self.addFromPath(name+ext,resource)
        if ext!='.mp3' and ext!='.wav': 
            try:
                olddir=os.getcwd()
                os.chdir(self.path)
                Song.convertToMP3(name+ext,name+'.mp3',ext[1:])
                ext='.mp3'
            finally:
                os.chdir=olddir
                self.recordings[(name+ext)]=resource

    def chceckAndDownloadFiles(self)->None:
        noteitems=list(self.notes.items())
        for k,v in noteitems:
            filepath=Path(self.path).joinpath(k)
            if not filepath.exists():
                n,ext=os.path.splitext(k)
                self.addnotes(v,n,ext)
        
        recordingitems=list(self.recordings.items())
        for k,v in recordingitems:
            filepath=Path(self.path).joinpath(k)
            if not filepath.exists():
                n,ext=os.path.splitext(k)
                self.addrecording(n,v,ext)

    def playrecording(self,name:str):
        
            if self.recordings[name]:
                filepath=Path(self.path).joinpath(name)
                if not filepath.exists():
                    n,ext=os.path.splitext(name)
                    self.addrecording(n,self.recordings[name],ext)
               
                pygame.mixer.music.stop()
                pygame.mixer.music.load(filepath)
                
                pygame.mixer.music.play()

       
    
    def playStartNotes(self,filename:str="startsound.wav"):
        if self.startsound:
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
    
    def deletefiles(self):
        if Path(self.path).exists():
            sh.rmtree(self.path)
