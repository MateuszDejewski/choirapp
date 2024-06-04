import shutil as sh
from pathlib import Path
import os
import pytube as pt
import requests
from music21 import note
from PIL import Image
from pydub import AudioSegment
from pydub.generators import Sine
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
pygame.mixer.init()



class Song:
    def __init__(self,name:str,author:str,choir,description:str="",notes=None,recordings=None,startnotes:str="",tags:list[str]=[]) -> None:
        self.name=name
        self.path = os.path.join("songs",choir.name,name)
        self.choir=choir
        self.author=author
        self.description=description
    
        self.notes=notes if notes else dict()
        self.recordings=recordings if recordings else dict()
         
        self.tags=[]
        self.setTags(tags)
        
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
        
        self.startnotes=""
        self.setStartnotes(startnotes)
        

    def setStartnotes(self,startnotes:str)->None:
        if startnotes!="":
            if self.startnotes==startnotes:
                return
            #creating startsound
            self.startnotes=startnotes
            try:
                self.startsound=Song.createStartNotes(startnotes)
                self.exportStartsound(self.startsound)
            except Exception:
                self.startsound=None
            
        else:
            self.startsound=None
    
    def exportStartsound(self,startsound:AudioSegment,filename:str="startsound.wav")->None:
        if not startsound:
            return
        try:
            filepath=Path(self.path).joinpath(filename)
            if filepath.exists():
                os.remove(str(filepath))
        
            oldpath=os.getcwd()
            os.chdir(self.path)
            startsound.export(filename,format='wav')
            os.chdir(oldpath)
        except Exception:
            raise RuntimeError("Unable to export startsound")

    def setTags(self,tags:list[str])->None:
        for tag in self.tags:
            self.choir.tagsdict[tag].remove(self)
            if self.choir.tagsdict[tag]==[]:
                del self.choir.tagsdict[tag]

        self.tags=tags
        for tag in self.tags:
            if tag in self.choir.tagsdict:
                self.choir.tagsdict[tag].append(self)
            else:
                self.choir.tagsdict[tag]=[self]


    def addFromPath(self,name:str,path:str)->str:
        oldname,ext= os.path.splitext(path)
        oldpath=os.getcwd()
        os.chdir(self.path)
        sh.copy(path,name+ext)
        os.chdir(oldpath)
        return ext
    
    def addFromInternet(self,name:str,url:str,ext:str)->str:
        data=requests.get(url)
        oldpath=os.getcwd()
        os.chdir(self.path)
        with open(name+ext, 'wb')as file:
            file.write(data.content)
        os.chdir(oldpath)
        return ext

    def addFromGoogleDrive(self,name:str,url:str,ext:str)->str:
        try:
            file_id = url.split('/d/')[1].split('/view')[0]
        except IndexError:
            raise ValueError("Invalid google drive share link")    
        direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        return self.addFromInternet(name,direct_link,ext)


    def addRecordingFromYoutube(self,file:str,url:str)->str:
            olddir=os.getcwd()
            os.chdir(self.path)

            yt = pt.YouTube(url)
            stream = yt.streams.filter(only_audio=True,file_extension='mp4').first()
            stream.download(filename="audio.mp4")

            Song.convertToMP3("audio.mp4",file,"mp4")
            os.remove("audio.mp4")
            os.chdir(olddir)
            return ".mp3"

    def convertToPDF(jpg_path:str, pdf_path:str)->None:
        image = Image.open(jpg_path)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(pdf_path, "PDF", resolution=100.0)  

    def addnotes(self,resource:str,name:str="",ext:str="")->None:
        if name=="":
            name=self.name+str(len(self.notes)+1)
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
        elif resource.startswith("www") or resource.startswith("http"):
            self.addFromInternet(name,resource,ext)
        else:
            ext = self.addFromPath(name,resource)
        if ext!='.pdf':
            try:
                olddir=os.getcwd()
                os.chdir(self.path)
                oldname=name+ext
                Song.convertToPDF(oldname,name+'.pdf')
                if oldname in self.notes:
                    del self.notes[oldname]
                    os.remove(oldname)
                ext='.pdf'
            except Exception:
                pass
            finally:
                os.chdir(olddir)
                
        self.notes[(name+ext)]=resource
    
    def convertToMP3(inputpath:str,outputpath:str,ext:str)->None:
        try:
            audio=AudioSegment.from_file(inputpath,format=ext)
            audio.export(outputpath,format='mp3')
        except Exception:
            raise RuntimeError("Unable to conver file")


    def addrecording(self,name:str,resource:str,ext:str="")->None:
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
        elif resource.startswith("https://www.youtube.com") or resource.startswith("https://youtu.be"):
            ext=self.addRecordingFromYoutube(name+".mp3",resource)
        elif resource.startswith("www") or resource.startswith("http"):
            self.addFromInternet(name,resource,ext)
        else:
            ext = self.addFromPath(name,resource)

        if ext!='.mp3' and ext!='.wav': 
            try:
                olddir=os.getcwd()
                os.chdir(self.path)
                oldname=name+ext
                Song.convertToMP3(oldname,name+'.mp3',ext[1:])
                if oldname in self.recordings:
                    del self.recordings[oldname]
                    os.remove(oldname)
                ext='.mp3'
            except Exception:
                pass
            finally:
                os.chdir(olddir)
        self.recordings[(name+ext)]=resource

    def checkAndDownloadFiles(self)->bool:
        if not Path(self.path).exists():
            os.makedirs(self.path)

        succes=True
        noteitems=list(self.notes.items())
        for k,v in noteitems:
            filepath=Path(self.path).joinpath(k)
            if not filepath.exists():
                n,ext=os.path.splitext(k)
                try:
                    self.addnotes(v,n,ext)
                except Exception:
                    succes=False

        recordingitems=list(self.recordings.items())
        for k,v in recordingitems:
            filepath=Path(self.path).joinpath(k)
            if not filepath.exists():
                n,ext=os.path.splitext(k)
                try:
                    self.addrecording(n,v,ext)
                except Exception:
                    succes=False
        return succes
    
    def checkFiles(self):
        noteitems=list(self.notes.items())
        for k,v in noteitems:
            filepath=Path(self.path).joinpath(k)
            if not filepath.exists():
                return False

        recordingitems=list(self.recordings.items())
        for k,v in recordingitems:
            filepath=Path(self.path).joinpath(k)
            if not filepath.exists():
                return False
        return True

    def playrecording(self,name:str)->None:
        
        if self.recordings[name]:
            filepath=Path(self.path).joinpath(name)
            if not filepath.exists():
                self.checkAndDownloadFiles()
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
            except Exception:
                raise RuntimeError("Unable to play recording")

       
    
    def playStartNotes(self,filename:str="startsound.wav")->None:
        if self.startsound:
            filepath=Path(self.path).joinpath(filename)
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
            except Exception:
                raise RuntimeError("Unable to play starting sounds")
        
    def strnotesToRealnotes(startnotes:str)->list[note.Note]:
        """
        Creates list of music21.notes from string A4 F#4 Bb3 F2
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
        """
        creating audio segment form given literal notes in str
        """
        try:
            notes=Song.strnotesToRealnotes(startnotes)
            return Song.realnotesTosound(notes)
        except Exception:
            raise RuntimeError("Unable to create starting notes\n Check given input and try again")  
        

    def deletefiles(self)->None:
        if Path(self.path).exists():
            try:
                sh.rmtree(self.path)
            except Exception:
                pass

    def __eq__(self,other:object)->bool:
        if isinstance(other,Song):
            return self.name==other.name
        return False