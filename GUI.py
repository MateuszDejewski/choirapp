from pathlib import Path
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QGridLayout,QStackedLayout,
    QLabel, QLineEdit, QTextEdit, 
    QPushButton, QCheckBox, QRadioButton,
    QListWidget, QListWidgetItem,
    QScrollArea,QSlider,
    QComboBox,
    QMessageBox,QDialog,
    QToolBar
)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QImage,QPixmap,QAction
from choir import Choir
from questionnaire import Questionnaire
from score import Score
from users import User,Singer,Conductor
from song import Song
from app import Choirapp
import fitz
from functools import partial
import keyring

class MainWindow(QMainWindow):
    def __init__(self,choirapp:Choirapp):
        super().__init__()
        self.setWindowTitle("Muzyczna Aplikacja")
        self.setGeometry(100, 100, 300, 200)
        self.choirapp:Choirapp=choirapp
        choirapp.read_choirs()
        self.choirs:list[Choir]=choirapp.choirs
        self.user:User=None
        self.choir:Choir=None
        
        self.logwidget=LoginWindow(self)
        self.setCentralWidget(self.logwidget)

        self.toolbar=QToolBar("MainToolbar")
        self.addToolBar(Qt.TopToolBarArea,self.toolbar)
        self.toolbar.setVisible(False)
    
    def closeEvent(self,event):
        self.choirapp.save_choirs()
        event.accept()

    
    def login_successful(self):
        self.init_toolbar()
        self.toolbar.setVisible(True)
        self.clear_central_widget()

    def init_toolbar(self):
        self.toolbar.clear()
        
        # Song list action
        song_list_action = QAction("Wyświetl listę utworów", self)
        song_list_action.triggered.connect(self.change_to_songlist)
        self.toolbar.addAction(song_list_action)

        # Score list action
        score_list_action = QAction("Wyświetl listę pieśni do nauki", self)
        score_list_action.triggered.connect(self.change_to_scorelist)
        self.toolbar.addAction(score_list_action)

        # Performance list action
        performance_list_action = QAction("Wyświetl listę występów", self)
        performance_list_action.triggered.connect(self.change_to_performancelist)
        self.toolbar.addAction(performance_list_action)

        # Manage choir action (only for conductor)
        if isinstance(self.user, Conductor):
            manage_choir_action = QAction("Zarządzaj chórem", self)
            manage_choir_action.triggered.connect(self.change_to_managechoir)
            self.toolbar.addAction(manage_choir_action)

        # Account management action
        account_action = QAction("Zarządzaj swoim kontem", self)
        account_action.triggered.connect(self.change_to_account)
        self.toolbar.addAction(account_action)

        # Logout action
        logout_action = QAction("Wyloguj się", self)
        logout_action.triggered.connect(self.logout)
        self.toolbar.addAction(logout_action)

    def clear_central_widget(self):
        self.takeCentralWidget()

    def change_to_songlist(self):
        self.song_list_widget = SongListWidget(self, self.choir.songs)
        self.setCentralWidget(self.song_list_widget)

    def change_to_scorelist(self):
        pass

    def change_to_performancelist(self):
        pass

    def change_to_managechoir(self):
        pass

    def change_to_account(self):
        self.accountwidget = UserdataWidget(self, self.user)
        self.setCentralWidget(self.accountwidget)

    def logout(self):
        self.user = None
        self.choir = None
        self.logwidget = LoginWindow(self)
        self.setCentralWidget(self.logwidget)
        self.toolbar.setVisible(False)

class SongWidget(QWidget):
    def __init__(self, song:Song|Score):
        super().__init__()
        
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
        loadpath= Path(self.song.path).joinpath(list(self.song.notes.keys())[0])
        self.pdf_document.load(str(loadpath))
        self.pdf_view.setDocument(self.pdf_document)
        
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
            self.questwid=QuestionnaireWidget(self.score.questionare)
            detaillayout.addWidget(self.questwid,i+1,0,4,2)

        layout.addLayout(zoomlayout)
        layout.addWidget(self.pdf_view)
        #layout.addWidget(self.scroll_area)
        layout.addLayout(detaillayout)
        self.setLayout(layout)


    def setpage(self):
        if len(self.song.notes)==0:
            self.pdf_label.setText("Nuty nie są dostępne")
        else:
            imagepath=Path(self.song.path).joinpath(list(self.song.notes.keys())[0])
            doc = fitz.open(imagepath)
            self.render_pdf_page(doc, 0)  # Render the first page
            self.pdf_label.setPixmap(self.current_pixmap)
        
    def render_pdf_page(self, doc, page_number):
        page = doc.load_page(page_number)
        pix = page.get_pixmap()
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        self.current_pixmap=QPixmap.fromImage(qimage)
    
    def update_zoom(self):
        zoom_factor=self.zoom_slider.value()/100
        self.pdf_view.setZoomFactor(zoom_factor)


    def play_recording(self,name:str):
        print("clicked ",name)
        self.song.playrecording(name)
    
    def play_startsound(self):
        self.song.playStartNotes()

class SongListWidget(QWidget):
    def __init__(self, mainwindow:MainWindow, listofsongs:list[Score]|list[Song]) -> None:
        super().__init__()
        self.mainwindow = mainwindow
        choir = mainwindow.choir
        self.user=self.mainwindow.user

        if len(choir.songs)==0:
            QMessageBox.warning(self,"Błąd","Nie żadnych ma pieśni.\nMożesz dodać nowe:)")
            self.addnewsong()
            return

        self.songlist = QListWidget()
        for song in listofsongs:
            item = QListWidgetItem(song.name)
            item.setData(1, song)
            self.songlist.addItem(item)
        self.songlist.itemDoubleClicked.connect(self.showSongDetail)
        self.songlist.currentRowChanged.connect(self.changedetails)

        self.song=choir.songs[0]          
        self.detaillayout = QGridLayout()
        self.detaillayout.setSpacing(10)
        self.namelabel = QLabel(self.song.name)
        self.namelabel.setAlignment(Qt.AlignCenter)
        self.detaillayout.addWidget(self.namelabel, 0, 0, 1, 2)
        self.detaillayout.addWidget(QLabel("autor:"), 1, 0)
        self.authorline = QLineEdit(self.song.author)
        self.authorline.setReadOnly(True)
        self.detaillayout.addWidget(self.authorline, 1, 1)
        self.detaillayout.addWidget(QLabel("opis:"), 2, 0)
        self.descline = QLineEdit(self.song.description)
        self.descline.setMinimumHeight(60)
        self.descline.setReadOnly(True)
        self.detaillayout.addWidget(self.descline, 2, 1, 2, 1)

        self.notes_label = QLineEdit()
        self.notes_label.setReadOnly(True)
        self.detaillayout.addWidget(self.notes_label, 4, 0, 1, 2)

        self.startsound_label = QLineEdit()
        self.startsound_label.setReadOnly(True)
        self.detaillayout.addWidget(self.startsound_label, 5, 0, 1, 2)

        self.detaillayout.addWidget(QLabel("Lista nagrań:"),6,0,1,2)

        self.recordinglist = QListWidget()
        self.detaillayout.addWidget(self.recordinglist, 7, 0, 3, 2)

        self.openbutton=QPushButton("Zobacz utwór")
        self.openbutton.clicked.connect(lambda: self.showSongDetail(self.songlist.currentItem()))
        self.detaillayout.addWidget(self.openbutton,11,0,1,2)

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
        if isinstance(self.song,Score):
            self.mainwindow.choir.scores.remove(self.song)    
        if isinstance(self.song,Song):
            self.song.deletefiles()
            self.mainwindow.choir.songs.remove(self.song)
        self.songlist.takeItem(self.songlist.currentRow())
        self.songlist.setCurrentRow(0)        

    def updateDetails(self):
        self.namelabel.setText(self.song.name)
        self.authorline.setText(self.song.author)
        self.descline.setText(self.song.description)
        
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
        self.updateDetails()

    def showSongDetail(self, songwid: QListWidgetItem):
        self.detailWidget = SongWidget(songwid.data(1))
        self.mainwindow.setCentralWidget(self.detailWidget)

class AddresourceDialog(QDialog):
    def __init__(self,windowtitle:str,namelabel:str):
        super().__init__()
        self.setWindowTitle(windowtitle)
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        
        self.name_label = QLabel(namelabel)
        self.name_input = QLineEdit()
        
        self.url_label = QLabel("Źródło: ")
        self.url_input = QLineEdit()
        
        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_resource)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.add_button)
        
        self.setLayout(layout)
        
        self.recording = None
    
    def add_resource(self):
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        
        if name and url:
            self.resource = (name, url)
            self.accept()
        else:
            QMessageBox.warning(self, "Błąd", "Wszystkie pola muszą być wypełnione!")

class AddSongWidget(QWidget):
    def __init__(self, mainwindow:MainWindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.choir = mainwindow.choir
        self.user=self.mainwindow.user
        
        self.setWindowTitle("Dodaj Piosenkę")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        self.name_label = QLabel("Nazwa piosenki:")
        self.name_input = QLineEdit()
        
        self.author_label = QLabel("Autor:")
        self.author_input = QLineEdit()
        
        self.description_label = QLabel("Opis:")
        self.description_input = QTextEdit()
             
        self.add_notes_button = QPushButton("Dodaj nuty")
        self.add_notes_button.clicked.connect(self.open_add_notes_dialog)
        
        self.notes_list = QListWidget()

        self.add_recording_button = QPushButton("Dodaj nagranie")
        self.add_recording_button.clicked.connect(self.open_add_recording_dialog)
        
        self.recordings_list = QListWidget()

        self.startingnotes_label = QLabel("Dźwieki poszątkowe: (np. A4 F#4 Bb3 F2)")
        self.startingnotes_imput = QLineEdit()
        
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
        layout.addWidget(QLabel("Lista nagrań"))
        layout.addWidget(self.recordings_list)
        layout.addWidget(self.add_recording_button)
        layout.addWidget(self.startingnotes_label)
        layout.addWidget(self.startingnotes_imput)
        layout.addWidget(self.add_song_button)
        
        self.setLayout(layout)
        
        self.recordings = {}
        self.notes={}
    
    def open_add_recording_dialog(self):
        dialog = AddresourceDialog("Dodawanie nagrania","Nazwa nagranie: ")
        if dialog.exec_():
            name, url = dialog.resource
            self.recordings[name] = url
            self.recordings_list.addItem(name)
    
    def open_add_notes_dialog(self):
        dialog = AddresourceDialog("Dodawanie nut","Nazwa pliku z nutami: ")
        if dialog.exec_():
            name, url = dialog.resource
            self.notes[name] = url
            self.notes_list.addItem(name)
    
    def add_song(self):
        name = self.name_input.text().strip()
        author = self.author_input.text().strip()
        description = self.description_input.toPlainText().strip()
        startnotes=self.startingnotes_imput.text().strip()
        if name in self.mainwindow.choir.songs:
            name=None

        if name:
            self.choir.addSong(name, author, description, self.notes, self.recordings,startnotes)
            self.mainwindow.setCentralWidget(SongListWidget(self.mainwindow,self.mainwindow.choir.songs))
        else:
            QMessageBox.warning(self, "Błąd", "Piosenka musi mieć nazwę")

class EditSongWidget(QWidget):
    def __init__(self, mainwindow: MainWindow, song: Song):
        super().__init__()
        self.mainwindow = mainwindow
        self.choir = mainwindow.choir
        self.user = self.mainwindow.user
        self.song = song

        self.setWindowTitle("Edytuj Piosenkę")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.name_label = QLabel("Nazwa piosenki:")
        self.name_input = QLineEdit(self.song.name)

        self.author_label = QLabel("Autor:")
        self.author_input = QLineEdit(self.song.author)

        self.description_label = QLabel("Opis:")
        self.description_input = QTextEdit(self.song.description)

        self.add_notes_button = QPushButton("Dodaj nuty")
        self.add_notes_button.clicked.connect(self.open_add_notes_dialog)

        self.notes_list = QListWidget()
        for note in self.song.notes.keys():
            self.notes_list.addItem(note)

        self.remove_notes_button = QPushButton("Usuń wybrane nuty")
        self.remove_notes_button.clicked.connect(self.remove_selected_notes)

        self.add_recording_button = QPushButton("Dodaj nagranie")
        self.add_recording_button.clicked.connect(self.open_add_recording_dialog)

        self.recordings_list = QListWidget()
        for recording in self.song.recordings.keys():
            self.recordings_list.addItem(recording)

        self.remove_recording_button = QPushButton("Usuń wybrane nagranie")
        self.remove_recording_button.clicked.connect(self.remove_selected_recording)

        self.startingnotes_label = QLabel("Dźwięki początkowe: (np. A4 F#4 Bb3 F2)")
        self.startingnotes_input = QLineEdit(self.song.startsound)

        self.save_button = QPushButton("Zapisz zmiany")
        self.save_button.clicked.connect(self.save_song)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Lista nut:"))
        notes_layout.addWidget(self.notes_list)
        notes_layout.addWidget(self.add_notes_button)
        notes_layout.addWidget(self.remove_notes_button)
        
        recordings_layout = QVBoxLayout()
        recordings_layout.addWidget(QLabel("Lista nagrań:"))
        recordings_layout.addWidget(self.recordings_list)
        recordings_layout.addWidget(self.add_recording_button)
        recordings_layout.addWidget(self.remove_recording_button)
        
        layout.addLayout(notes_layout)
        layout.addLayout(recordings_layout)
        layout.addWidget(self.startingnotes_label)
        layout.addWidget(self.startingnotes_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.recordings = self.song.recordings.copy()
        self.notes = self.song.notes.copy()

    def open_add_recording_dialog(self):
        dialog = AddresourceDialog("Dodawanie nagrania", "Nazwa nagrania: ")
        if dialog.exec_():
            name, url = dialog.resource
            self.recordings[name] = url
            self.recordings_list.addItem(name)

    def open_add_notes_dialog(self):
        dialog = AddresourceDialog("Dodawanie nut", "Nazwa pliku z nutami: ")
        if dialog.exec_():
            name, url = dialog.resource
            self.notes[name] = url
            self.notes_list.addItem(name)

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

    def save_song(self):
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

        self.mainwindow.setCentralWidget(SongListWidget(self.mainwindow, self.mainwindow.choir.songs))

class QuestionnaireWidget(QWidget):
    def __init__(self,questionnaire: Questionnaire):
        super().__init__()
        self.questionnaire = questionnaire

        layout = QVBoxLayout()

        # Question label
        self.question_label = QLabel(self.questionnaire.question)
        layout.addWidget(self.question_label)

        # Answer widgets
        self.answer_widgets = []
        if self.questionnaire.multipleChoice:
            for answer in self.questionnaire.possibleAnswers:
                checkbox = QCheckBox(answer)
                self.answer_widgets.append(checkbox)
                layout.addWidget(checkbox)
        else:
            self.answer_group = QVBoxLayout()
            for answer in self.questionnaire.possibleAnswers:
                radiobutton = QRadioButton(answer)
                self.answer_widgets.append(radiobutton)
                self.answer_group.addWidget(radiobutton)
            layout.addLayout(self.answer_group)

        # New answer input
        if self.questionnaire.addingNewAnswers:
            self.new_answer_input = QLineEdit()
            layout.addWidget(self.new_answer_input)

        # Submit button
        self.submit_button = QPushButton("Submit Answer")
        self.submit_button.clicked.connect(self.submit_answer)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        

    def submit_answer(self):
        user_answer = []
        if self.questionnaire.multipleChoice:
            for widget in self.answer_widgets:
                if widget.isChecked():
                    user_answer.append(widget.text())
        else:
            for widget in self.answer_widgets:
                if widget.isChecked():
                    user_answer = widget.text()
                    break

        if self.questionnaire.addingNewAnswers and self.new_answer_input.text():
            new_answer = self.new_answer_input.text()
            user_answer.append(new_answer)
            self.questionnaire.addPossibleAnswer(new_answer)

        self.questionnaire.addUserAnswer("User", user_answer)
        for widget in self.answer_widgets:
            widget.setChecked(False)

class CreatechoirWidget(QWidget):
    def __init__(self,mainwindow:MainWindow):
        super().__init__()
        self.mainwindow=mainwindow
        creationlayot=QGridLayout()
        
        titlelabel=QLabel("Utwórz nowy chór")
        titlelabel.setAlignment(Qt.AlignCenter)
        creationlayot.addWidget(titlelabel,0,0,1,2)

        creationlayot.addWidget(QLabel("Uwaga: Za chwilę utworzysz nowy chór i konto dyrygenta nim zarządzające.\n Jeśli chcesz dołączyć do istniejącego chóru skontaktuj się ze swoim dyrygentem."),1,0,2,2)

        creationlayot.addWidget(QLabel("Nazwa chóru: "),3,0)
        self.choirname=QLineEdit()
        creationlayot.addWidget(self.choirname,3,1)

        creationlayot.addWidget(QLabel("Nazwa użytkownika: "),4,0)
        self.username=QLineEdit()
        creationlayot.addWidget(self.username,4,1)

        creationlayot.addWidget(QLabel("Login użytkownika: "),5,0)
        self.userlogin=QLineEdit()
        creationlayot.addWidget(self.userlogin,5,1)

        creationlayot.addWidget(QLabel("Hasło: "),6,0)
        self.password1=QLineEdit()
        self.password1.setEchoMode(QLineEdit.Password)
        creationlayot.addWidget(self.password1,6,1)

        creationlayot.addWidget(QLabel("Powtórz hasło: "),7,0)
        self.password2=QLineEdit()
        self.password2.setEchoMode(QLineEdit.Password)
        creationlayot.addWidget(self.password2,7,1)

        self.createbutton=QPushButton("Utwórz chór")
        self.createbutton.clicked.connect(self.createnewchoir)
        creationlayot.addWidget(self.createbutton,8,1)
        self.cancelbutton=QPushButton("Anuluj")
        self.cancelbutton.clicked.connect(self.cancel)
        creationlayot.addWidget(self.cancelbutton,8,0)

        self.setLayout(creationlayot)

    def cancel(self):
        self.mainwindow.setCentralWidget(LoginWindow(self.mainwindow))    

    def createnewchoir(self):
            choir_name = self.choirname.text().strip()
            username = self.username.text().strip()
            userlogin = self.userlogin.text().strip()
            password1 = self.password1.text().strip()
            password2 = self.password2.text().strip()

            if not choir_name:
                QMessageBox.warning(self, "Błąd", "Nazwa chóru nie może być pusta.")
                return
            if not username:
                QMessageBox.warning(self, "Błąd", "Nazwa użytkownika nie może być pusta.")
                return
            if not userlogin:
                QMessageBox.warning(self, "Błąd", "Login użytkownika nie może być pusty.")
                return
            if not password1 or not password2:
                QMessageBox.warning(self, "Błąd", "Hasło nie może być puste.")
                return
            if password1 != password2:
                QMessageBox.warning(self, "Błąd", "Hasła nie są zgodne.")
                return
           
            newchoir=Choir(choir_name)
            conductor=Conductor(username,userlogin,password1)
            newchoir.conductors.append(conductor)
            try:
                self.mainwindow.choirapp.add_choir(newchoir)
            except ValueError:
                QMessageBox.warning(self, "Błąd", "Nazwa chóru nie jest unikalna")
                return
            self.mainwindow.choir=newchoir
            self.mainwindow.user=conductor
            self.mainwindow.setCentralWidget(MenuWidget(self.mainwindow))

class MenuWidget(QWidget):
    def __init__(self,mainWindow:MainWindow) -> None:
        super().__init__()
        self.mainwindow=mainWindow
        self.user=self.mainwindow.user
        
        self.mainwindow.login_successful()

        menulayout=QVBoxLayout()

        menulayout.addWidget(QLabel("Jesteś zalogowany jako "+self.user.name))


        self.songlistbutton=QPushButton("Wyświetl listę utworów")
        self.songlistbutton.clicked.connect(self.change_to_songlist)
        menulayout.addWidget(self.songlistbutton)

        self.scorelistbutton=QPushButton("Wyświetl listę pieśni do nauki")
        self.scorelistbutton.clicked.connect(self.change_to_scorelist)
        menulayout.addWidget(self.scorelistbutton)

        self.performancelistbutton=QPushButton("Wyświetl listę występów")
        self.performancelistbutton.clicked.connect(self.change_to_performancelist)
        menulayout.addWidget(self.performancelistbutton)

        if isinstance(self.user,Conductor):
            self.managechoirbutton=QPushButton("Zarządzaj chórem")
            self.managechoirbutton.clicked.connect(self.change_to_managechoir)
            menulayout.addWidget(self.managechoirbutton)
        
        self.accountbutton=QPushButton("Zarządzaj swoim kontem")
        self.accountbutton.clicked.connect(self.change_to_account)
        menulayout.addWidget(self.accountbutton)
        
        self.logoutbutton=QPushButton("Wyloguj się")
        self.logoutbutton.clicked.connect(self.logout)
        menulayout.addWidget(self.logoutbutton)

        self.setLayout(menulayout)

    def change_to_songlist(self):
        self.song_list_widget = SongListWidget(self.mainwindow,self.mainwindow.choir.songs)
        self.mainwindow.setCentralWidget(self.song_list_widget)

    def change_to_scorelist(self):
        pass

    def change_to_performancelist(self):
        pass

    def change_to_managechoir(self):
        pass

    def change_to_account(self):
        self.accountwidget=UserdataWidget(self.mainwindow,self.user)
        self.mainwindow.setCentralWidget(self.accountwidget)

    def logout(self):
        self.mainwindow.setCentralWidget(LoginWindow(self.mainwindow))

class LoginWindow(QWidget):
    def __init__(self,mainwindow:MainWindow):
        super().__init__()
        self.mainwindow=mainwindow
        choir_label=QLabel("Wybierz chór")
        self.choir_list=QComboBox()
        for choir in mainwindow.choirs:
            self.choir_list.addItem(choir.name,choir)

        username_label = QLabel("Nazwa użytkownika")
        self.username_input = QLineEdit()

        password_label = QLabel("Hasło")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Zaloguj się")
        self.login_button.clicked.connect(self.handle_login)

        username_layout = QHBoxLayout()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)

        password_layout = QHBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        self.createchoirbutton=QPushButton("Utwórz nowy chór")
        self.createchoirbutton.clicked.connect(self.open_creation_viev)

        main_layout = QVBoxLayout()
        main_layout.addWidget(choir_label)
        main_layout.addWidget(self.choir_list)
        main_layout.addLayout(username_layout)
        main_layout.addLayout(password_layout)
        main_layout.addWidget(self.login_button)
        main_layout.addSpacing(30)
        main_layout.addWidget(self.createchoirbutton)
        
        self.setLayout(main_layout)

    def findUser(self,username:str):
        
        for singer in self.choir.singers:
                if singer.login==username:
                    return singer
        for conductor in self.choir.conductors:
                if conductor.login==username:
                    return conductor
                
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if keyring.get_password("app",username)==password:
            self.choir:Choir=self.choir_list.currentData()
            self.user=self.findUser(username)
            if self.user==None:
                QMessageBox.warning(self, "Błąd", "Nieprawidłowe dane logowania lub wybrany chór.")
                return
            self.mainwindow.user=self.user 
            self.mainwindow.choir=self.choir
            menu=MenuWidget(self.mainwindow)
            self.mainwindow.setCentralWidget(menu)
        else:    
            QMessageBox.warning(self, "Błąd", "Nieprawidłowa nazwa użytkownika lub hasło.")      
    
    def open_creation_viev(self):
        self.creation=CreatechoirWidget(self.mainwindow)
        self.mainwindow.setCentralWidget(self.creation)

class UserdataWidget(QWidget):
    def __init__(self, mainwindow:MainWindow,user:User) -> None:
        super().__init__()
        self.mainwidnow=mainwindow
        self.user=user

        layout=QGridLayout()
        layout.addWidget(QLabel("Nazwa użytkownika: "),0,0)
        self.usernameline=QLineEdit(self.user.name)
        layout.addWidget(self.usernameline,0,1)

        layout.addWidget(QLabel("Login: "),1,0)
        self.loginline=QLineEdit(self.user.login)
        layout.addWidget(self.loginline,1,1)

        layout.addWidget(QLabel("Obecne hasło: "),2,0)
        self.password1=QLineEdit()
        self.password1.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password1,2,1)

        layout.addWidget(QLabel("Nowe hasło: "),3,0)
        self.password2=QLineEdit()
        self.password2.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password2,3,1)

        layout.addWidget(QLabel("Powtórz nowe hasło: "),4,0)
        self.password3=QLineEdit()
        self.password3.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password3,4,1)

        if isinstance(self.user,Singer):
            layout.addWidget(QLabel("Podstawowy głos: "),5,0)
            self.voiceline=QLineEdit(self.user.basicvoice)
            self.voiceline.setReadOnly(True)
            layout.addWidget(self.voiceline,5,1)

        self.savebutton=QPushButton("Zapisz zmiany")
        self.savebutton.clicked.connect(self.save)
        layout.addWidget(self.savebutton,5,0,1,2)

        self.setLayout(layout)

    def save(self):
        username=self.usernameline.text().strip()
        if username!=self.user.name:
            if not username:
                QMessageBox.warning(self, "Błąd", "Nazwa użytkownika nie może być pusta.")
                return
            else:
                self.user.name=username
        
        login=self.loginline.text().strip()
        if login!=self.user.login: 
            if not login:
                QMessageBox.warning(self, "Błąd", "Login nie może być pusty.")
                return
            elif not keyring.get_credential("app",login):
                QMessageBox.warning(self, "Błąd", "Login musi być unikalny.")
                return
            else:
                self.user.changelogin(login)

        if self.password1.isModified():
            password1=self.password1.text().strip()
            password2=self.password2.text().strip()
            password3=self.password3.text().strip()

            if password1!=keyring.get_password("app",self.user.login):
                QMessageBox.warning(self, "Błąd", "Hasło jest niepoprawne.")
                return
            if not password3 or not password2:
                QMessageBox.warning(self, "Błąd", "Nowe hasło nie może być puste.")
                return
            if password2 != password3:
                QMessageBox.warning(self, "Błąd", "Nowe hasła nie są zgodne.")
                return

            self.user.changepassword(password3)
        
        self.mainwidnow.setCentralWidget(MenuWidget(self.mainwidnow))













if __name__=='__main__':
    # choir=Choir("karmel")
    # # # choir.addSong(name="Chwała Tobie Królu Wieków",
    # # #               notes={"Chwała Tobie Królu Wieków.pdf":"C:/moje_prace/schola/nuty/Chwala_Tobie_Slowo_Boze.pdf"},
    # # #               recordings={"tenor.wav":"https://drive.google.com/file/d/1nKHHkY50q3uyoShJNviIPex8UXy5HTAL/view?usp=drive_link",
    # # #                           "Bas.wav":"https://drive.google.com/file/d/1DipBRnOjiDvpTHeQBKIb8ZbuPW-PX_dq/view?usp=drive_link",
    # # #                           "Przykldowe_wykonanie.wav":'https://www.youtube.com/watch?v=AI2hcI3uoO8'},#"Przykladowe wykonanie.mp3":'https://www.youtube.com/watch?v=AI2hcI3uoO8'},
    # # #                 startnotes="A5 Eb5 C5 C4")
    
    # choir.addSong("Deus miserere mei",
    #               notes={"Deus miserere mei.pdf":"https://drive.google.com/file/d/1h6V1yRi1uSyMP1YHK5n8fcsl5mlljqq0/view?usp=drive_link"},
    #               recordings={
    #                   "Sopran.acc":"https://drive.google.com/file/d/1g9FEs0OxgxZZUwo5x0sk23FiwIyXnDZ0/view?usp=drive_link",
    #                   "Alt.acc":"https://drive.google.com/file/d/1BzCMb9iEYrNv10ERbw9X02PVvHjnD5RW/view?usp=sharing",
    #                   "Tenor.acc":"https://drive.google.com/file/d/1Cs7y40SvwXcz82mxaBpp8CPBK847IHEC/view?usp=drive_link",
    #                   "Bas.acc":"https://drive.google.com/file/d/1thVVlh2VCG6eebwNyCUdWFJSNVYwWTfX/view?usp=drive_link"
    #               })   
    # choir.addSong("Gaude Mater Polonia",
    #               notes={"Gaude Mater Polonia.pdf":"https://drive.google.com/file/d/1xy2Z2af-N1hMCYRuzwvIEPWzvIuwm-xO/view?usp=drive_link"},
    #               recordings={
    #                   "Sopran.mp3":"https://drive.google.com/file/d/1zDzagXS1ml6RViRIAxQKjU2z0S05kCIV/view?usp=drive_link",
    #                   "Alt.mp3": "https://drive.google.com/file/d/1pQMvL4acGuUpOjMQjOkpR_1ys98LhOAc/view?usp=drive_link",
    #                   "Tenor.mp3": "https://drive.google.com/file/d/1lTL_n4SHS_VXXUOn5cpT7btmFO6W9lfk/view?usp=drive_link",
    #                   "Bas.mp3":"https://drive.google.com/file/d/1l1K79I9jCQb7yeloApeQfRgwdtumy2Eq/view?usp=drive_link"
    #               }
    # )
    # app=Choirapp([choir])

    # app.choirs[0].singers.append(Singer("Zuzia","zuzu","zuzu","sopran"))
    # app.choirs[0].conductors.append(Conductor("Mateusz","matdej3459","dejefa"))
    # app.save_choirs()
    # app=Choirapp()
    # app.read_choirs()
    # app.save_choirs()

    gui = QApplication(sys.argv)
    wind=MainWindow(Choirapp())
    wind.show()
    sys.exit(gui.exec())