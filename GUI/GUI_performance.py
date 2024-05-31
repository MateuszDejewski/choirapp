from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem,
    QMessageBox,QDateEdit
)
from GUI.GUI_scores import AddScoreWidget
from GUI.GUI_songs import SongWidget
from src.performance import Performance
from src.users import User,Singer,Conductor
import pendulum

class PerformanceWidget(QWidget):
    def __init__(self, performance:Performance,user:User) -> None:
        super().__init__()
        self.user=user
        self.performance=performance
        
        layout=QVBoxLayout()
        self.namelebel=QLabel(performance.name)
        self.namelebel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.namelebel)

        self.date=QDateEdit()
        self.date.setReadOnly(True)
        self.date.setDisplayFormat("dd.MM.yyyy")
        self.date.setButtonSymbols(QDateEdit.NoButtons)
        self.date.setDate(performance.date)

        layout.addWidget(QLabel("Data: "))
        layout.addWidget(self.date)

        layout.addWidget(QLabel("Szczegóły występu:"))
        self.desc=QLineEdit()
        self.desc.setReadOnly(True)
        layout.addWidget(self.desc)

        self.songlist = QListWidget()
        for score in self.performance.songs: 
            item=QListWidgetItem(score.song.name)
            item.setData(1,score)
            self.songlist.addItem(item)

        self.songlist.itemDoubleClicked.connect(self.openscore)
        self.songlist.sortItems()

        layout.addWidget(QLabel("Lista utworów:"))
        layout.addWidget(self.songlist)

        self.singerlist = QListWidget()
        for singer in self.performance.singers: 
            self.singerlist.addItem(QListWidgetItem(singer.name))
        self.singerlist.sortItems()
        
        layout.addWidget(QLabel("Lista śpiewających"))
        layout.addWidget(self.singerlist)
        self.setLayout(layout)

    def openscore(self,songwid: QListWidgetItem):
        self.scoreview = SongWidget(songwid.data(1),self.user)
        self.scoreview.show()
        

class AddPerforamnceWidget(QWidget):
    def __init__(self,mainwidnow)-> None:
        super().__init__()
        self.mainwindow=mainwidnow
        self.performance=None
        layout=QGridLayout()
        layout.addWidget(QLabel("Nazwa występu: "),0,0)
        self.name_input=QLineEdit()
        layout.addWidget(self.name_input,0,1,1,2)

        layout.addWidget(QLabel("Data występu"),1,0)
        self.date_input=QDateEdit()
        self.date_input.setDate(pendulum.today())
        self.date_input.setCalendarPopup(True)
        self.date_input.setMinimumWidth(90)
        layout.addWidget(self.date_input,1,1)

        layout.addWidget(QLabel("Szczegóły dotyczące występu:"),2,0)
        self.details_input=QLineEdit()
        layout.addWidget(self.details_input,2,1)

        self.addScorebutton=QPushButton("Dodaj aranżację pieśni")
        self.addScorebutton.clicked.connect(self.addScore)
        layout.addWidget(self.addScorebutton,5,0)


        self.scorelist = QListWidget()
        for score in self.mainwindow.choir.scores:
            item = QListWidgetItem(score.song.name) 
            item.setData(1, score)
            self.scorelist.addItem(item)
        
        layout.addWidget(self.scorelist,6,0,3,1)

        
        self.addEndSongbutton=QPushButton("Dodaj utwór na koniec")
        self.addEndSongbutton.clicked.connect(self.addSongEnd)
        self.addBeforeSongbutton=QPushButton("Dodaj utwór przed wybranym")
        self.addBeforeSongbutton.clicked.connect(self.addBeforeSong)
        self.removeSongbutton=QPushButton("Usuń utwór z występu")
        self.removeSongbutton.clicked.connect(self.removeSong)
        
        songbuttonlayout=QVBoxLayout()
        songbuttonlayout.addWidget(self.addEndSongbutton)
        songbuttonlayout.addWidget(self.addBeforeSongbutton)
        songbuttonlayout.addWidget(self.removeSongbutton)
        layout.addLayout(songbuttonlayout,6,1,3,1)

        self.performance_songlist = QListWidget()
        layout.addWidget(self.performance_songlist,6,2,3,1)

        self.singerlist = QListWidget()
        for singer in self.mainwindow.choir.singers:
            item = QListWidgetItem(singer.name) 
            item.setData(1, singer)
            self.singerlist.addItem(item)
        self.singerlist.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.singerlist,9,0,3,1)

        self.addAllSingersbutton=QPushButton("Dodaj wszystkich chórzystów")
        self.addAllSingersbutton.clicked.connect(self.addAllSingers)
        self.addSelectedSingersbutton=QPushButton("Dodaj wybranych chórzystów")
        self.addSelectedSingersbutton.clicked.connect(self.addSelectedSingers)
        self.removeSelectedSingersbutton=QPushButton("Usuń wybranych chórzystów z występu")
        self.removeSelectedSingersbutton.clicked.connect(self.removeSelectedSingers)
        
        singerbuttonlayout=QVBoxLayout()
        singerbuttonlayout.addWidget(self.addAllSingersbutton)
        singerbuttonlayout.addWidget(self.addSelectedSingersbutton)
        singerbuttonlayout.addWidget(self.removeSelectedSingersbutton)
        layout.addLayout(singerbuttonlayout,9,1,3,1)

        self.performance_singerlist = QListWidget()
        self.performance_singerlist.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.performance_singerlist,9,2,3,1)

        generalbuttonlayout=QHBoxLayout()
        self.addPerformanceButton=QPushButton("Zapisz wystąpienie")
        self.addPerformanceButton.clicked.connect(self.addPerformance)
        self.cancelbutton=QPushButton("anuluj")
        self.cancelbutton.clicked.connect(self.cancel)
        generalbuttonlayout.addWidget(self.cancelbutton)
        generalbuttonlayout.addWidget(self.addPerformanceButton)

        layout.addLayout(generalbuttonlayout,12,0,1,3)

        self.setLayout(layout)

    def addScore(self):
        self.addscorewid=AddScoreWidget(self.mainwindow)
        self.addscorewid.available_checkbox.hide()
        self.addscorewid.singerlist.hide()
        self.addscorewid.cancelbutton.hide()
        self.addscorewid.inthebackground=True
        self.addscorewid.setWindowTitle("Dodawanie aranżacji")
        self.addscorewid.show()
        self.addscorewid.hideEvent= lambda event:self.refreshscorelist()

    def refreshscorelist(self):
        newscore=self.mainwindow.choir.scores[-1]
        additem=QListWidgetItem(newscore.song.name)
        additem.setData(1,newscore)
        self.scorelist.addItem(additem)

    
    def setPerformance(self, performance):
        self.performance = performance
        self.name_input.setText(performance.name)
        self.date_input.setDate(performance.date)
        self.details_input.setText(performance.details)
        
        self.performance_songlist.clear()
        for song in performance.songs:
            item = QListWidgetItem(song.song.name)
            item.setData(1, song)
            self.performance_songlist.addItem(item)
            
        # Remove items from scorelist if they are in performance
        for index in range(self.scorelist.count() - 1, -1, -1):
            item = self.scorelist.item(index)
            score = item.data(1)
            if score in performance.songs:
                self.scorelist.takeItem(index)

        self.performance_singerlist.clear()
        for singer in performance.singers:
            item = QListWidgetItem(singer.name)
            item.setData(1, singer)
            self.performance_singerlist.addItem(item)

        # Remove items from singerlist if they are in performance
        for index in range(self.singerlist.count() - 1, -1, -1):
            item = self.singerlist.item(index)
            singer = item.data(1)
            if singer in performance.singers:
                self.singerlist.takeItem(index)


    def addSongEnd(self):
        item = self.scorelist.takeItem(self.scorelist.currentRow())
        if item:
            self.performance_songlist.addItem(item)

    def addBeforeSong(self):
        item = self.scorelist.takeItem(self.scorelist.currentRow())
        if item:
            self.performance_songlist.insertItem(self.performance_songlist.currentRow(), item)

    def removeSong(self):
        item = self.performance_songlist.takeItem(self.performance_songlist.currentRow())
        if item:
            self.scorelist.addItem(item)

    def addAllSingers(self):
        while self.singerlist.count() > 0:
            item = self.singerlist.takeItem(0)
            self.performance_singerlist.addItem(item)
    
    def addSelectedSingers(self):
        for item in self.singerlist.selectedItems():
            row = self.singerlist.row(item)
            self.singerlist.takeItem(row)
            self.performance_singerlist.addItem(item)

    def removeSelectedSingers(self):
        for item in self.performance_singerlist.selectedItems():
            row = self.performance_singerlist.row(item)
            self.performance_singerlist.takeItem(row)
            self.singerlist.addItem(item)

    def addPerformance(self):
        name = self.name_input.text()
        date = self.date_input.date().toPython()
        details = self.details_input.text()

        if not name:
            QMessageBox.warning(self, "Błąd", "Nazwa występu nie może być pusta.")
            return

        if self.performance_songlist.count() == 0:
            QMessageBox.warning(self, "Błąd", "Występ musi zawierać przynajmniej jeden utwór.")
            return

        songs = []
        for index in range(self.performance_songlist.count()):
            item = self.performance_songlist.item(index)
            song = item.data(1)
            songs.append(song)

        singers = []
        for index in range(self.performance_singerlist.count()):
            item = self.performance_singerlist.item(index)
            singer = item.data(1)
            singers.append(singer)

        if self.performance:
            self.performance.name = name
            self.performance.date = date
            self.performance.details = details
            self.performance.songs = songs
            self.performance.singers = singers
            message = "Występ został zaktualizowany pomyślnie."
        else:
            performance = Performance(name=name, date=date, details=details, songs=songs, conductor=self.mainwindow.user, singers=singers)
            self.mainwindow.choir.performances.append(performance)
            message = "Występ został dodany pomyślnie."
        
        self.mainwindow.setCentralWidget(PerformancelistWidget(self.mainwindow, self.mainwindow.choir.performances))
        
    
    def cancel(self):
        self.mainwindow.setCentralWidget(PerformancelistWidget(self.mainwindow,self.mainwindow.choir.performances))

class PerformancelistWidget(QWidget):
    def __init__(self, mainwidnow, performances:list[Performance]) -> None:
        super().__init__()
        self.mainwindow=mainwidnow
        self.performances=performances
        self.user=self.mainwindow.user
        if len(performances)==0:
            if isinstance(self.user,Conductor):
                QMessageBox.warning(self,"Błąd","Nie ma żadnych wystąpień.\nMożesz dodać nowe:)")
                self.addperformance()
                return
            else:
                QMessageBox.warning(self,"Błąd","Nie ma żadnych wystąpień do wyświetenia.")
                return
                   

        self.performancelist = QListWidget()
        for perf in self.performances:
            item = QListWidgetItem(perf.name)
            item.setData(1, perf)
            self.performancelist.addItem(item)
        self.performancelist.setCurrentRow(0)
        self.performancelist.currentRowChanged.connect(self.changedetails)

        listlayout=QVBoxLayout()
        listlayout.addWidget(QLabel("Lista wystąpień"))
        listlayout.addWidget(self.performancelist)

        self.detailwidget=PerformanceWidget(self.performances[0],self.user)

        self.centrallayout=QHBoxLayout()
        self.centrallayout.addLayout(listlayout)
        self.centrallayout.addWidget(self.detailwidget)
       
        wholelayout=QVBoxLayout()
        wholelayout.addLayout(self.centrallayout)

        if isinstance(self.user,Conductor):
            buttonlayout=QHBoxLayout()
            self.addbutton=QPushButton("Dodaj nowe wystąpienie")
            self.addbutton.clicked.connect(self.addperformance)
            buttonlayout.addWidget(self.addbutton)

            self.editbutton=QPushButton("Edytuj wystąpienie")
            self.editbutton.clicked.connect(self.editperformance)
            buttonlayout.addWidget(self.editbutton)
            
            self.removebutton=QPushButton("Usuń wystąpienie")
            self.removebutton.clicked.connect(self.removeperformance)
            buttonlayout.addWidget(self.removebutton)
            
            wholelayout.addLayout(buttonlayout)
        
        self.setLayout(wholelayout)
 
    def addperformance(self):
        self.addperfwid=AddPerforamnceWidget(self.mainwindow)
        self.mainwindow.setCentralWidget(self.addperfwid)

    def editperformance(self):
        self.addperfwid=AddPerforamnceWidget(self.mainwindow)
        self.addperfwid.setPerformance(self.performancelist.currentItem().data(1))
        self.mainwindow.setCentralWidget(self.addperfwid)
    
    def removeperformance(self):
        currentperf=self.performancelist.currentItem().data(1)
        reply = QMessageBox.question(self, 'Potwierdzenie usunięcia',
                                         'Czy na pewno chcesz usunąć występ '+currentperf.name+"?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return        
        perf=self.performancelist.takeItem(self.performancelist.currentRow()).data(1)
        self.mainwindow.choir.performances.remove(perf)

    def changedetails(self):
        self.centrallayout.removeWidget(self.detailwidget)
        self.detailwidget.hide()
        if self.performancelist.currentItem():
            self.detailwidget=PerformanceWidget(self.performancelist.currentItem().data(1),self.user)
        self.centrallayout.addWidget(self.detailwidget)