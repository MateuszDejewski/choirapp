import shutil as sh
from pathlib import Path
import os
import pytube as pt
import requests

class Song:
    def __init__(self,name:str,author:str="",notes:list[str]=[],recordings:list[str]=[],startnotes:str="") -> None:
        self.name=name
        self.path="songs/"+name.replace("s+",'_')
        self.author=author
        self.notes=notes
        self.recordings=recordings
        self.startnotes=startnotes
        if not Path("songs").exists():
            os.mkdir("songs")
        if not Path(self.path).exists():
            oldpath=os.getcwd()
            os.chdir("songs")
            os.mkdir(self.path[6:])
            os.chdir(oldpath)

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
            oldpath=os.getcwd()
            os.chdir(self.path)
            os.rename(out_file, new_file)
            os.chdir(oldpath)

    def addnotes(self,resource:str,ext:str=""):
        name=self.name+str(len(self.notes)+1)
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
            self.notes.append((name+ext,resource))
        else:
            ext = self.addFromPath(name+ext,resource)
        self.notes.append( ((name+ext),resource) )
    
    def addrecording(self,name:str,resource:str,ext:str=""):
        if resource.startswith("https://drive.google.com"):
            self.addFromGoogleDrive(name=name,url=resource,ext=ext)
            self.notes.append((name+ext,resource))
        elif resource.startswith("https://www.youtube.com"):
            self.addRecordingFromYoutube(name,resource,ext)
        else:
            ext = self.addFromPath(name+ext,resource)
        self.recordings.append(((name+ext),resource) )



if __name__=='__main__':
    chwala=Song("Chwała Tobie Królu Wieków")
    chwala.addnotes("C:/moje_prace/schola/nuty/Chwala_Tobie_Slowo_Boze.pdf",)
    chwala.addrecording("tenor","https://drive.google.com/file/d/1nKHHkY50q3uyoShJNviIPex8UXy5HTAL/view?usp=drive_link",'.wav')
    chwala.addrecording("Przykładowe wykonanie",'https://www.youtube.com/watch?v=AI2hcI3uoO8')

    panie=Song("Panie nie jestem godzien")
    panie.addrecording("Całość",'https://www.youtube.com/watch?v=bOCuY_M9s90')
