from __future__ import annotations
from pathlib import Path
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QGridLayout,QFormLayout,
    QLabel, QLineEdit, QTextEdit, 
    QPushButton, QCheckBox, QRadioButton,
    QListWidget, QListWidgetItem,
    QScrollArea,QSlider,
    QComboBox,
    QMessageBox,QDialog,
    QToolBar,QDialogButtonBox,QLCDNumber
)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QImage,QPixmap,QAction
import pygame
from GUI_quest import QuestionnaireWidget
from choir import Choir
from questionnaire import Questionnaire
from score import Score
from users import User,Singer,Conductor
from song import Song
from app import Choirapp
from functools import partial
import os

class SongWidget(QWidget):
    def __init__(self, song:Song|Score, user:User):
        super().__init__()
        self.user=user
        if isinstance(song,Score):
            self.score:Score=song
            self.song:Song=song.song
        else:
            self.score=None
            self.song=song

        self.setWindowTitle("Szczegóły Piosenki")
        layout = QHBoxLayout()
        
        self.pdf_view=QPdfView()
        self.pdf_view.setMinimumWidth(200)
        self.pdf_document=QPdfDocument(self)
        if len(self.song.notes):
            loadpath= os.path.join(self.song.path,list(self.song.notes.keys())[0])
            self.pdf_document.load(loadpath)
        self.pdf_view.setDocument(self.pdf_document)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        
        self.zoom_slider = QSlider(Qt.Vertical)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(10)
        self.update_zoom()
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        zoomlayout=QVBoxLayout()
        zoomlayout.addWidget(QLabel("zoom in"))
        zoomlayout.addWidget(self.zoom_slider)
        zoomlayout.addWidget(QLabel("zoom out"))
        

        detaillayout=QGridLayout()
        namelabel=QLabel(self.song.name)
        namelabel.setAlignment(Qt.AlignCenter)
        detaillayout.addWidget(namelabel,0,0,1,2)
        detaillayout.addWidget(QLabel("autor:"),1,0)
        authorline=QLineEdit(self.song.author)
        authorline.setReadOnly(True)
        detaillayout.addWidget(authorline,1,1)
        detaillayout.addWidget(QLabel("opis:"),2,0)
        descline=QLineEdit(self.song.description)
        descline.setReadOnly(True)
        detaillayout.addWidget(descline,3,0,2,2)
        if self.score:
            detaillayout.addWidget(QLabel("uwagi dyrygenta:"),5,0)
            commentline=QLineEdit(self.score.conductorcomments)
            commentline.setReadOnly(True)
            commentline.setFixedSize(200,50)
            detaillayout.addWidget(commentline,6,0,2,2)
        
        i=8
        for record in list(self.song.recordings.keys()):
            lebel=QLabel(record)
            detaillayout.addWidget(lebel,i,0)
            play_button=QPushButton("odtwórz")
            play_button.clicked.connect(partial(self.play_recording,record))
            detaillayout.addWidget(play_button,i,1)
            i+=1
        if self.song.startsound or (self.score and self.score.startsound):
            startsound_button=QPushButton("Odtwórz dźwięki początkowe")
            startsound_button.clicked.connect(self.play_startsound)
            detaillayout.addWidget(startsound_button,i,0,1,2)
        if self.score:
            self.questwid=QuestionnaireWidget(self.score.questionare,user)
            detaillayout.addWidget(self.questwid,i+1,0,4,2)
        
        layout.addLayout(zoomlayout)
        layout.addWidget(self.pdf_view)
        layout.addLayout(detaillayout)
        self.setLayout(layout)
        self.current_page=0
    
    def update_zoom(self):
        zoom_factor=self.zoom_slider.value()/100
        self.pdf_view.setZoomFactor(zoom_factor)

    def play_recording(self,name:str):
        self.song.playrecording(name)
    
    def play_startsound(self):
        self.song.playStartNotes()

    def closeEvent(self,event):
        pygame.mixer.music.stop()
        event.accept()

class SongListWidget(QWidget):
    def __init__(self, mainwindow:MainWindow, listofsongs:list[Score]|list[Song]) -> None:
        super().__init__()
        self.mainwindow = mainwindow
        choir = mainwindow.choir
        self.user=self.mainwindow.user
        if len(listofsongs)==0:
            if isinstance(self.user,Conductor):
                QMessageBox.warning(self,"Błąd","Nie żadnych ma pieśni.\nMożesz dodać nowe:)")
                self.addnewsong()
                return
            else:
                QMessageBox.warning(self,"Błąd","Nie żadnych ma pieśni do wyświetenia.")
                return
            
        self.isScore=isinstance(listofsongs[0],Score)

        self.songlist = QListWidget()
        for song in listofsongs:
            item = QListWidgetItem(song.song.name) if self.isScore else QListWidgetItem(song.name)
            item.setData(1, song)
            self.songlist.addItem(item)
        self.songlist.itemDoubleClicked.connect(self.showSongDetail)
        self.songlist.currentRowChanged.connect(self.changedetails)

        self.song=listofsongs[0]
        if self.isScore:
            self.score=song
            self.song=self.song.song       
        self.detaillayout = QGridLayout()
        self.detaillayout.setSpacing(10)
        self.namelabel = QLabel(self.song.name)
        self.namelabel.setAlignment(Qt.AlignCenter)
        self.detaillayout.addWidget(self.namelabel, 0, 0, 1, 2)
        
        row=1
        if self.isScore:
            self.detaillayout.addWidget(QLabel("uwagi dyrygenta"), 1, 0)
            self.conductorcomment_output = QLineEdit(self.score.conductorcomments)
            self.conductorcomment_output.setReadOnly(True)
            self.detaillayout.addWidget(self.conductorcomment_output, 1, 1)
            self.detaillayout.addWidget(QLabel("Transpozycja:"), 2, 0)
            self.transposition_output = QLCDNumber()
            self.transposition_output.display(self.score.transposition)
            self.detaillayout.addWidget(self.transposition_output, 2, 1)
            self.availablelabel = QLineEdit()
            self.availablelabel.setReadOnly(True)
            self.detaillayout.addWidget(self.availablelabel, 3, 0, 1, 2)
            row=4


        self.detaillayout.addWidget(QLabel("autor:"), row, 0)
        self.authorline = QLineEdit(self.song.author)
        self.authorline.setReadOnly(True)
        self.detaillayout.addWidget(self.authorline, row, 1)
        row+=1
        self.detaillayout.addWidget(QLabel("opis:"), row, 0)
        self.descline = QLineEdit(self.song.description)
        self.descline.setMinimumHeight(60)
        self.descline.setReadOnly(True)
        self.detaillayout.addWidget(self.descline, row, 1, 2, 1)
        row+=1
        self.notes_label = QLineEdit()
        self.notes_label.setReadOnly(True)
        self.detaillayout.addWidget(self.notes_label, row, 0, 1, 2)
        row+=1
        self.startsound_label = QLineEdit()
        self.startsound_label.setReadOnly(True)
        self.detaillayout.addWidget(self.startsound_label, row, 0, 1, 2)
        row+=1
        self.detaillayout.addWidget(QLabel("Lista nagrań:"),row,0,1,2)
        row+=1
        self.recordinglist = QListWidget()
        self.detaillayout.addWidget(self.recordinglist, row, 0, 3, 2)
        row+=3
        self.openbutton=QPushButton("Zobacz utwór")
        self.openbutton.clicked.connect(lambda: self.showSongDetail(self.songlist.currentItem()))
        self.detaillayout.addWidget(self.openbutton,row,0,1,2)

        if isinstance(self.user,Conductor):
            self.editbutton=QPushButton("Edytuj utwór")
            self.editbutton.clicked.connect(self.editsong)
            self.detaillayout.addWidget(self.editbutton,12,0,1,2)

            self.deletebutton=QPushButton("Usuń utwór")
            self.deletebutton.clicked.connect(self.deletesong)
            self.detaillayout.addWidget(self.deletebutton,13,0,1,2)

        layout = QHBoxLayout()
        helplayout = QVBoxLayout()
        helplayout.addWidget(QLabel("Lista pieśni chóru " + choir.name))
        helplayout.addWidget(self.songlist)
        if isinstance(self.user,Conductor):
            self.addnewsongbutton=QPushButton("Dodaj nową pieść")
            self.addnewsongbutton.clicked.connect(self.addnewsong)
            helplayout.addWidget(self.addnewsongbutton)
        layout.addLayout(helplayout)
        layout.addLayout(self.detaillayout)
        self.setLayout(layout)
        
        self.songlist.setCurrentRow(0)

    def addnewsong(self):
        self.mainwindow.setCentralWidget(AddSongWidget(self.mainwindow))

    def editsong(self):
        song = self.songlist.currentItem().data(1)
        self.mainwindow.setCentralWidget(EditSongWidget(self.mainwindow, song))
        
    def deletesong(self):
        if self.isScore:
            self.mainwindow.choir.scores.remove(self.songlist.currentItem().data(1))    
        else:
            self.song.deletefiles()
            self.mainwindow.choir.songs.remove(self.song)
        self.songlist.takeItem(self.songlist.currentRow())
        self.songlist.setCurrentRow(0)        

    def updateDetails(self):
        self.namelabel.setText(self.song.name)
        self.authorline.setText(self.song.author)
        self.descline.setText(self.song.description)

        if self.isScore:
            self.conductorcomment_output.setText(self.score.conductorcomments)
            self.transposition_output.display(self.score.transposition)
            self.availablelabel.setText("Utwór dospępny dla wszysktich chórzystów" if self.score.avaliable else "Utwór dostępny tylko dla wybranych chórzystów")

        if len(self.song.notes) > 0:
            notes_text = "Nuty są dostępne"
        else:
            notes_text = "Nuty są niedostępne"
        self.notes_label.setText(notes_text)

        if self.song.startsound is not None:
            startsound_text = "Odtworzenie dźwięków początkowych jest dostępne"
        else:
            startsound_text = "Odtworzenie dźwięków początkowych jest niedostępne"
        self.startsound_label.setText(startsound_text)

        self.recordinglist.clear()
        for record in list(self.song.recordings.keys()):
            self.recordinglist.addItem(record)

    def changedetails(self):
        self.song = self.songlist.currentItem().data(1)
        if self.isScore:
            self.score=self.score
            self.song=self.song.song
        self.updateDetails()

    def showSongDetail(self, songwid: QListWidgetItem):
        self.detailWidget = SongWidget(songwid.data(1),self.user)
        self.mainwindow.setCentralWidget(self.detailWidget)

class AddresourceDialog(QDialog):
    def __init__(self,windowtitle:str,namelabel:str,graphic:bool):
        super().__init__()
        self.setWindowTitle(windowtitle)
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        
        self.name_label = QLabel(namelabel)
        self.name_input = QLineEdit()
        
        self.url_label = QLabel("Źródło: ")
        self.url_input = QLineEdit()
        self.ext_combo=QComboBox()
        if graphic:
            self.ext_combo.addItems([".pdf",".jpg","inne (podaj pełną nazwę z rozszerzeniem)"])
        else:
            self.ext_combo.addItems([".mp3",".wav",'.acc','.m4a',"inne (podaj pełną nazwę z rozszerzeniem)"])
        
        self.ext_combo.setEditable(True)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_resource)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.ext_combo)
        layout.addWidget(self.add_button)
        
        self.setLayout(layout)
        
        self.recording = None
    
    def add_resource(self):
        ext = self.ext_combo.currentText()
        
        name = self.name_input.text().strip()
        if ext=="inne (podaj pełną nazwę z rozszerzeniem)":
            name,ext =os.path.splitext(name)
        
        if name.find('.')!=-1:
            QMessageBox.warning(self, "Błąd", "Nazwa nie może zawierać kropki")

        url = self.url_input.text().strip()
        
        if name and url:
            self.resource = (name, url, ext)
            self.accept()
        else:
            QMessageBox.warning(self, "Błąd", "Wszystkie pola muszą być wypełnione!")

class AddSongWidget(QWidget):
    def __init__(self, mainwindow:MainWindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.choir = mainwindow.choir
        self.user=self.mainwindow.user
        
        self.setWindowTitle("Dodaj utwór")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        self.name_label = QLabel("Nazwa utworu:")
        self.name_input = QLineEdit()
        
        self.author_label = QLabel("Autor:")
        self.author_input = QLineEdit()
        
        self.description_label = QLabel("Opis:")
        self.description_input = QTextEdit()
             
        self.add_notes_button = QPushButton("Dodaj nuty")
        self.add_notes_button.clicked.connect(self.open_add_notes_dialog)
        self.remove_notes_button = QPushButton("Usuń wybrane nuty")
        self.remove_notes_button.clicked.connect(self.remove_selected_notes)
        
        self.notes_list = QListWidget()

        self.add_recording_button = QPushButton("Dodaj nagranie")
        self.add_recording_button.clicked.connect(self.open_add_recording_dialog)
        self.remove_recording_button = QPushButton("Usuń wybrane nagranie")
        self.remove_recording_button.clicked.connect(self.remove_selected_recording)
       
        
        self.recordings_list = QListWidget()

        self.startingnotes_label = QLabel("Dźwieki poszątkowe: (np. A4 F#4 Bb3 F2)")
        self.startingnotes_input = QLineEdit()
        
        self.add_song_button = QPushButton("Zatwierdź wszystko i dodaj piosenkę")
        self.add_song_button.clicked.connect(self.add_song)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Lista nut: "))
        layout.addWidget(self.notes_list)
        layout.addWidget(self.add_notes_button)
        layout.addWidget(self.remove_notes_button)
        layout.addWidget(QLabel("Lista nagrań"))
        layout.addWidget(self.recordings_list)
        layout.addWidget(self.add_recording_button)
        layout.addWidget(self.remove_recording_button)
        layout.addWidget(self.startingnotes_label)
        layout.addWidget(self.startingnotes_input)
        layout.addWidget(self.add_song_button)
        
        self.setLayout(layout)
        
        self.recordings = {}
        self.notes={}
    
    def open_add_recording_dialog(self):
        dialog = AddresourceDialog("Dodawanie nagrania","Nazwa nagranie: ",False)
        if dialog.exec_():
            name, url, ext = dialog.resource
            filename=name+ext if ext!="inne" else name
            self.recordings[filename] = url
            self.recordings_list.addItem(filename)
    
    def open_add_notes_dialog(self):
        dialog = AddresourceDialog("Dodawanie nut","Nazwa pliku z nutami: ",True)
        if dialog.exec_():
            name, url,ext = dialog.resource
            filename=name+ext if ext!="inne" else name
            self.notes[filename] = url
            self.notes_list.addItem(filename)
    
    def remove_selected_notes(self):
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            name = item.text()
            del self.notes[name]
            self.notes_list.takeItem(self.notes_list.row(item))

    def remove_selected_recording(self):
        selected_items = self.recordings_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            name = item.text()
            del self.recordings[name]
            self.recordings_list.takeItem(self.recordings_list.row(item))

    def add_song(self):
        name = self.name_input.text().strip()
        author = self.author_input.text().strip()
        description = self.description_input.toPlainText().strip()
        startnotes=self.startingnotes_input.text().strip()
        if name in self.mainwindow.choir.songs:
            name=None
        if name:
            self.choir.addSong(name, author, description, self.notes, self.recordings,startnotes)
            self.mainwindow.setCentralWidget(SongListWidget(self.mainwindow,self.mainwindow.choir.songs))
        else:
            QMessageBox.warning(self, "Błąd", "Piosenka musi mieć nazwę")

# class EditSongWidget(QWidget):
#     def __init__(self, mainwindow: MainWindow, song: Song):
#         super().__init__()
#         self.mainwindow = mainwindow
#         self.choir = mainwindow.choir
#         self.user = self.mainwindow.user
#         self.song = song

#         self.setWindowTitle("Edytuj Piosenkę")
#         self.setGeometry(100, 100, 400, 300)

#         layout = QVBoxLayout()

#         self.name_label = QLabel("Nazwa piosenki:")
#         self.name_input = QLineEdit(self.song.name)

#         self.author_label = QLabel("Autor:")
#         self.author_input = QLineEdit(self.song.author)

#         self.description_label = QLabel("Opis:")
#         self.description_input = QTextEdit(self.song.description)

#         self.add_notes_button = QPushButton("Dodaj nuty")
#         self.add_notes_button.clicked.connect(self.open_add_notes_dialog)

#         self.notes_list = QListWidget()
#         for note in self.song.notes.keys():
#             self.notes_list.addItem(note)

#         self.remove_notes_button = QPushButton("Usuń wybrane nuty")
#         self.remove_notes_button.clicked.connect(self.remove_selected_notes)

#         self.add_recording_button = QPushButton("Dodaj nagranie")
#         self.add_recording_button.clicked.connect(self.open_add_recording_dialog)

#         self.recordings_list = QListWidget()
#         for recording in self.song.recordings.keys():
#             self.recordings_list.addItem(recording)

#         self.remove_recording_button = QPushButton("Usuń wybrane nagranie")
#         self.remove_recording_button.clicked.connect(self.remove_selected_recording)

#         self.startingnotes_label = QLabel("Dźwięki początkowe: (np. A4 F#4 Bb3 F2)")
#         self.startingnotes_input = QLineEdit(self.song.startnotes)

#         self.save_button = QPushButton("Zapisz zmiany")
#         self.save_button.clicked.connect(self.save_song)

#         layout.addWidget(self.name_label)
#         layout.addWidget(self.name_input)
#         layout.addWidget(self.author_label)
#         layout.addWidget(self.author_input)
#         layout.addWidget(self.description_label)
#         layout.addWidget(self.description_input)
        
#         notes_layout = QVBoxLayout()
#         notes_layout.addWidget(QLabel("Lista nut:"))
#         notes_layout.addWidget(self.notes_list)
#         notes_layout.addWidget(self.add_notes_button)
#         notes_layout.addWidget(self.remove_notes_button)
        
#         recordings_layout = QVBoxLayout()
#         recordings_layout.addWidget(QLabel("Lista nagrań:"))
#         recordings_layout.addWidget(self.recordings_list)
#         recordings_layout.addWidget(self.add_recording_button)
#         recordings_layout.addWidget(self.remove_recording_button)
        
#         layout.addLayout(notes_layout)
#         layout.addLayout(recordings_layout)
#         layout.addWidget(self.startingnotes_label)
#         layout.addWidget(self.startingnotes_input)
#         layout.addWidget(self.save_button)

#         self.setLayout(layout)

#         self.recordings = self.song.recordings.copy()
#         self.notes = self.song.notes.copy()

#     def open_add_recording_dialog(self):
#         dialog = AddresourceDialog("Dodawanie nagrania", "Nazwa nagrania: ")
#         if dialog.exec_():
#             name, url = dialog.resource
#             self.recordings[name] = url
#             self.recordings_list.addItem(name)

#     def open_add_notes_dialog(self):
#         dialog = AddresourceDialog("Dodawanie nut", "Nazwa pliku z nutami: ")
#         if dialog.exec_():
#             name, url = dialog.resource
#             self.notes[name] = url
#             self.notes_list.addItem(name)

#     def remove_selected_notes(self):
#         selected_items = self.notes_list.selectedItems()
#         if not selected_items:
#             return
#         for item in selected_items:
#             name = item.text()
#             del self.notes[name]
#             self.notes_list.takeItem(self.notes_list.row(item))

#     def remove_selected_recording(self):
#         selected_items = self.recordings_list.selectedItems()
#         if not selected_items:
#             return
#         for item in selected_items:
#             name = item.text()
#             del self.recordings[name]
#             self.recordings_list.takeItem(self.recordings_list.row(item))

#     def save_song(self):
#         name = self.name_input.text().strip()
#         author = self.author_input.text().strip()
#         description = self.description_input.toPlainText().strip()
#         startnotes = self.startingnotes_input.text().strip()

#         if not name:
#             QMessageBox.warning(self, "Błąd", "Piosenka musi mieć nazwę")
#             return

#         self.song.name = name
#         self.song.author = author
#         self.song.description = description
#         self.song.notes = self.notes
#         self.song.recordings = self.recordings
#         self.song.startsound = startnotes

#         self.mainwindow.setCentralWidget(SongListWidget(self.mainwindow, self.mainwindow.choir.songs))

class EditSongWidget(AddSongWidget):
    def __init__(self, mainwindow: MainWindow,song:Song):
        super().__init__(mainwindow)
        self.song=song
        for note in self.song.notes.keys():
            self.notes_list.addItem(note)
        for recording in self.song.recordings.keys():
            self.recordings_list.addItem(recording)
        
        self.name_input.setText(self.song.name)
        self.author_input.setText(self.song.author)
        self.description_input.setText(self.song.description)
        self.startingnotes_input.setText(self.song.startnotes)
    
    def add_song(self):
        name = self.name_input.text().strip()
        author = self.author_input.text().strip()
        description = self.description_input.toPlainText().strip()
        startnotes = self.startingnotes_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Błąd", "Piosenka musi mieć nazwę")
            return

        self.song.name = name
        self.song.author = author
        self.song.description = description
        self.song.notes = self.notes
        self.song.recordings = self.recordings
        self.song.startsound = startnotes
        
        self.song.chceckAndDownloadFiles()

        self.mainwindow.setCentralWidget(SongListWidget(self.mainwindow, self.mainwindow.choir.songs))