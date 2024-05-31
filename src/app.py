import os
import pickle

from src.choir import Choir

class Choirapp:
    def __init__(self,choirs:list[Choir]=[],backupdir:str=None) -> None:
        self.choirs=choirs
        if not backupdir or backupdir=="":
            self.backupdir=os.getcwd()
        else:
            self.backupdir=backupdir

    def save_choirs(self,filename:str="choirapp_backup"):
        filepath=os.path.join(self.backupdir,filename)
        with open(filepath,'wb') as file:
            pickle.dump(self.choirs,file)
    
    def read_choirs(self,filename:str="choirapp_backup"):
        filepath = os.path.join(self.backupdir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as file:
                self.choirs = pickle.load(file)

    def add_choir(self,choir:Choir):
        for ch in self.choirs:
            if ch.name==choir.name:
                raise ValueError("Name is not unique")
        self.choirs.append(choir)

    def delete_choir(self,choir:Choir):
        if choir in self.choirs:
            self.choirs.remove(choir)
        for song in choir.songs:
            choir.deleteSong(song)