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
from moviepy.editor import *

#pydub.AudioSegment.ffmpeg="C:/Users/mateu/ffmpeg-7.0-full_build/bin"


class Song:
    def __init__(self,name:str,author:str="",description:str="",notes=None,recordings=None,startnotes:str="") -> None:
        self.name=name
        self.path = "songs\\"+name
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
        if not Path("songs").exists():
            os.mkdir("songs")
        if not Path(self.path).exists():
            oldpath=os.getcwd()
            os.chdir("songs")
            os.mkdir(self.path[6:])
            os.chdir(oldpath)
        pygame.mixer.init()
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
            #download_audio_from_youtube(url,file)
            olddir=os.getcwd()
            os.chdir(self.path)

            yt = pt.YouTube(url)
            stream = yt.streams.filter(only_audio=True,file_extension='mp4').first()
            download_path = stream.download(filename="audio.mp4")

            import subprocess
            output_file = os.path.splitext(file)[0]+".wav"
            command = ["ffmpeg", "-i", download_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", output_file]
            subprocess.call(command)
            # audio_clip = AudioFileClip(download_path)
            # audio_clip.write_audiofile(file, codec='pcm_s16le')
            
            #Usuń tymczasowy plik MP4
            os.remove(download_path)
            os.chdir(olddir)
            return '.wav'
            

    def addnotes(self,resource:str,name:str="",ext:str=""):
        if name=="":
            name=self.name+str(len(self.notes)+1)
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
        else:
            ext = self.addFromPath(name,resource)
        self.notes[(name+ext)]=resource
    
    def addrecording(self,name:str,resource:str,ext:str=""):
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
        elif resource.startswith("https://www.youtube.com") or resource.startswith("https://youtu.be"):
            ext=self.addRecordingFromYoutube(name+".wav",resource)
        else:
            ext = self.addFromPath(name+ext,resource)
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

                # wave_obj=sa.WaveObject.from_wave_file(str(filepath))
                # if self.playobj and self.playobj.is_playing():
                #     self.playobj.stop()
                # self.playobj=wave_obj.play()
                
                pygame.mixer.music.stop()
                pygame.mixer.music.load(filepath)
                
                pygame.mixer.music.play()

                print("plaied")
       
    
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
