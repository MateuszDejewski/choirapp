from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QListWidget,QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QGridLayout,QFormLayout,
    QLabel, QLineEdit, QTextEdit, 
    QPushButton, QCheckBox, QRadioButton,
    QListWidget, QListWidgetItem,
    QSpinBox,QMessageBox
)
from score import Score
from GUI_songs import SongListWidget
from song import Song

class AddScoreWidget(QWidget):
    def __init__(self,mainwidnow:Mainwindow):
        super().__init__()
        self.mainwindow=mainwidnow
        self.songs=self.mainwindow.choir.songs
        self.inthebackground=False #avoid changing main window

        layout=QGridLayout()
        layout.addWidget(QLabel("Wybierz utwór"),0,0,1,2)
        self.songlist = QListWidget()
        for song in self.songs:
            item = QListWidgetItem(song.name)
            item.setData(1, song)
            self.songlist.addItem(item)
        self.songlist.setSelectionMode(QListWidget.SingleSelection)

        layout.addWidget(self.songlist,1,0,3,2)
        layout.addWidget(QLabel("Komentarz dotyczący wykonania:"),4,0,1,2)
        self.comment=QLineEdit()
        layout.addWidget(self.comment,5,0,1,2)

        layout.addWidget(QLabel("Wybierz liczbę półtonów do transponacji:"),6,0)

        self.number_input = QSpinBox()
        self.number_input.setMinimum(-12)
        self.number_input.setMaximum(12) 
        layout.addWidget(self.number_input,6,1)

        self.available_checkbox = QCheckBox("Udostępnij tylko wybranym chórzystom")
        self.available_checkbox.stateChanged.connect(self.avaliable_changed)
        layout.addWidget(self.available_checkbox,7,0,1,2)

        self.singerlist = QListWidget()
        for singer in self.mainwindow.choir.singers:
            item = QListWidgetItem(singer.name)
            item.setData(1, singer)
            self.singerlist.addItem(item)
        self.singerlist.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.singerlist,8,0,3,2)
        self.singerlist.setVisible(False)

        buttonlayout=QHBoxLayout()

        self.cancelbutton=QPushButton("Powrót")
        self.cancelbutton.clicked.connect(self.cancel)
        buttonlayout.addWidget(self.cancelbutton)

        self.addbutton=QPushButton("Dodaj aranżację do nauki")
        self.addbutton.clicked.connect(self.addscore)
        buttonlayout.addWidget(self.addbutton)

        layout.addLayout(buttonlayout,11,0,1,2)

        self.setLayout(layout)

    def avaliable_changed(self):
        self.singerlist.setVisible(self.available_checkbox.isChecked())

    def cancel(self):
        self.mainwindow.setCentralWidget(ScorelistWidget(self.mainwindow,self.mainwindow.choir.scores))


    def addscore(self):
        selected_song_item = self.songlist.currentItem()
        if not selected_song_item:
            QMessageBox.warning(self,"Błąd","Nie wybrano żadnej pieśni")
            return
        
        selected_song = selected_song_item.data(1)
        comment = self.comment.text()
        transposition = self.number_input.value()
        
        selected_singers = []
        if self.available_checkbox.isChecked():
            selected_singers_items = self.singerlist.selectedItems()
            selected_singers = [item.data(1) for item in selected_singers_items]
            self.mainwindow.choir.addScore(selected_song, comment, transposition,False, selected_singers)
        else:
            self.mainwindow.choir.addScore(selected_song, comment, transposition, True)
        if not self.inthebackground:
            self.mainwindow.setCentralWidget(ScorelistWidget(self.mainwindow,self.mainwindow.choir.getScoresForSinger(self.mainwindow.user)))
        else:
            self.hide()

class EditScoreWidget(QWidget):
    def __init__(self,mainwidnow:Mainwindow,score:Score):
        super().__init__()
        self.mainwindow=mainwidnow
        self.score=score
        self.songs=self.mainwindow.choir.songs

        layout=QGridLayout()
        layout.addWidget(QLabel("Wybierz utwór"),0,0,1,2)
        self.songlist = QListWidget()
        for song in self.songs:
            item = QListWidgetItem(song.name)
            item.setData(1, song)
            self.songlist.addItem(item)
            if song==score.song:
                self.songlist.setCurrentItem(item)
        self.songlist.setSelectionMode(QListWidget.SingleSelection)

        layout.addWidget(self.songlist,1,0,3,2)
        layout.addWidget(QLabel("Komentarz dotyczący wykonania:"),4,0,1,2)
        self.comment=QLineEdit(self.score.conductorcomments)
        layout.addWidget(self.comment,5,0,1,2)

        layout.addWidget(QLabel("Wybierz liczbę półtonów do transponacji:"),6,0)

        self.number_input = QSpinBox()
        self.number_input.setValue(score.transposition)
        self.number_input.setMinimum(-12)
        self.number_input.setMaximum(12) 
        layout.addWidget(self.number_input,6,1)

        self.available_checkbox = QCheckBox("Udostępnij tylko wybranym chórzystom")
        self.available_checkbox.stateChanged.connect(self.avaliable_changed)
        layout.addWidget(self.available_checkbox,7,0,1,2)

        self.singerlist = QListWidget()
        for singer in self.mainwindow.choir.singers:
            item = QListWidgetItem(singer.name)
            item.setData(1, singer)
            self.singerlist.addItem(item)
            if singer in self.score.forUsers:
                item.setSelected(True)
        self.singerlist.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.singerlist,8,0,3,2)
        self.available_checkbox.setChecked(not self.score.avaliable)

        buttonlayout=QHBoxLayout()
        self.addbutton=QPushButton("Powrót")
        self.addbutton.clicked.connect(self.cancel)
        buttonlayout.addWidget(self.addbutton)

        self.addbutton=QPushButton("Zapisz zmiany")
        self.addbutton.clicked.connect(self.save)
        buttonlayout.addWidget(self.addbutton)

        layout.addLayout(buttonlayout,11,0,1,2)
        self.setLayout(layout)

    def avaliable_changed(self):
        self.singerlist.setVisible(self.available_checkbox.isChecked())

    def cancel(self):
        self.mainwindow.setCentralWidget(ScorelistWidget(self.mainwindow,self.mainwindow.choir.scores))

    def save(self):
        selected_song_item = self.songlist.currentItem()
        if not selected_song_item:
            QMessageBox.warning(self,"Błąd","Nie wybrano żadnej pieśni")
            return
        
        selected_song = selected_song_item.data(1)
        comment = self.comment.text()
        transposition = self.number_input.value()
        avaliable=not self.available_checkbox.isChecked()
        selected_singers = []
        if not avaliable:
            selected_singers_items = self.singerlist.selectedItems()
            selected_singers = [item.data(1) for item in selected_singers_items]

        self.score.song=selected_song
        self.score.conductorcomments=comment
        if self.score.transposition!=transposition:
            self.score.transposition=transposition
            self.score.startsound=Score.transposeStartingNotes(self.score.song.startnotes,transposition)
        self.score.avaliable=avaliable
        if not avaliable:
            self.score.forUsers=selected_singers 
        self.mainwindow.setCentarlWidget(ScorelistWidget(self.mainwindow,self.mainwindow.choir.getScoresForSinger(self.mainwindow.user)))

class ScorelistWidget(SongListWidget):
    def __init__(self, mainwindow:MainWindow, listofsongs:list[Score]) -> None:
        super().__init__(mainwindow,listofsongs)

    def addnewsong(self):
        self.addWidget=AddScoreWidget(self.mainwindow)
        self.mainwindow.setCentralWidget(self.addWidget)

    def editsong(self):
        self.editwidget=EditScoreWidget(self.mainwindow,self.songlist.currentItem().data(1))
        self.mainwindow.setCentralWidget(self.editwidget)       




        
