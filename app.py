import os
import pickle

class Choirapp:
    def __init__(self,choirs=[],backupdir:str=None) -> None:
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