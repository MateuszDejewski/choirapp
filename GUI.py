from pathlib import Path
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QGridLayout,QStackedLayout,
    QLabel, QLineEdit, 
    QPushButton, QCheckBox, QRadioButton,
    QListWidget, QListWidgetItem,
    QScrollArea,QSlider,
    QComboBox,
    QMessageBox
)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QImage,QPixmap
from choir import Choir
from conductor import Conductor
from questionnaire import Questionnaire
from score import Score
from singer import Singer
from song import Song
from app import Choirapp
import fitz
from functools import partial
import keyring

class SongWidget(QWidget):
    def __init__(self, song:Song|Score):
        super().__init__()
        if isinstance(song,Song):
            self.score=Score(song)
            self.song=song
        else:
            self.score=song
            self.song=song.song
        self.setWindowTitle("Szczegóły Piosenki")
        layout = QHBoxLayout()
        
        self.pdf_view=QPdfView()
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
        detaillayout.addWidget(QLabel("author:"),1,0)
        authorline=QLineEdit(self.song.author)
        authorline.setReadOnly(True)
        detaillayout.addWidget(authorline,1,1)
        detaillayout.addWidget(QLabel("description:"),2,0)
        descline=QLineEdit(self.song.description)
        descline.setReadOnly(True)
        detaillayout.addWidget(descline,3,0,2,2)
        detaillayout.addWidget(QLabel("conductor comments:"),5,0)
        commentline=QLineEdit(self.score.conductorcomments)
        commentline.setReadOnly(True)
        commentline.setFixedSize(200,50)
        detaillayout.addWidget(commentline,6,0,2,2)
        
        i=8
        for record in list(self.song.recordings.keys()):
            lebel=QLabel(record)
            detaillayout.addWidget(lebel,i,0)
            play_button=QPushButton("play")
            play_button.clicked.connect(partial(self.play_recording,record))
            detaillayout.addWidget(play_button,i,1)
            i+=1
        
        startsound_button=QPushButton("Play starting notes")
        startsound_button.clicked.connect(self.play_startsound)
        detaillayout.addWidget(startsound_button,i,0,1,2)
        
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
    def __init__(self,mainwindow) -> None:
        super().__init__()
        self.mainwindow=mainwindow
        choir=mainwindow.choir
        self.songlist=QListWidget()
        for song in choir.songs:
            item = QListWidgetItem(song.name)
            item.setData(1,song)
            self.songlist.addItem(item)
        self.songlist.itemDoubleClicked.connect(self.showSongDetail)

        layout=QVBoxLayout()
        layout.addWidget(QLabel("Lista pieśni chóru "+choir.name))
        layout.addWidget(self.songlist)
        self.setLayout(layout)

    def showSongDetail(self,songwid:QListWidgetItem):
        self.detailWidget=SongWidget(songwid.data(1))
        # self.mainwindow.mainlayout.addWidget(self.detailWidget)
        # self.mainwindow.mainlayout.setCurrentWidget(self.detailWidget)
        self.mainwindow.setCentralWidget(self.detailWidget)

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

      
class LoginWindow(QWidget):
    def __init__(self,mainwindow):
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
        print("find")
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
            self.song_list_widget = SongListWidget(self.mainwindow)
            self.mainwindow.setCentralWidget(self.song_list_widget)
        else:    
            QMessageBox.warning(self, "Błąd", "Nieprawidłowa nazwa użytkownika lub hasło.")
        
        
    def open_creation_viev(self):
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
        creationlayot.addWidget(self.createbutton,8,0,1,2)

        container=QWidget()
        container.setLayout(creationlayot)
        self.mainwindow.setCentralWidget(container)
        

    def createnewchoir(self):
            print("test1")
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
            print("test2")
            newchoir=Choir(choir_name)
            conductor=Conductor(username,userlogin,password1)
            newchoir.conductors.append(conductor)
            try:
                self.mainwindow.choirapp.addchoir(newchoir)
            except ValueError:
                QMessageBox.warning(self, "Błąd", "Nazwa chóru nie jest unikalna")
                return
            self.mainwindow.choir=newchoir
            self.mainwindow.setCentralWidget(SongListWidget(self.mainwindow))
        
    
        


class MainWindow(QMainWindow):
    def __init__(self,choirapp):
        super().__init__()
        self.setWindowTitle("Muzyczna Aplikacja")
        self.setGeometry(100, 100, 300, 200)
        self.choirapp=choirapp
        choirapp.read_choirs()
        self.choirs=choirapp.choirs
        if len(self.choirs)>0:
            self.choir=choirapp.choirs[0]
        
        self.logwidget=LoginWindow(self)
        self.setCentralWidget(self.logwidget)
    
    def closeEvent(self,event):
        self.choirapp.save_choirs()
        event.accept()


if __name__=='__main__':
    # choir=Choir("karmel")
    # choir.addSong(name="Chwała Tobie Królu Wieków",
    #               notes={"Chwała Tobie Królu Wieków.pdf":"C:/moje_prace/schola/nuty/Chwala_Tobie_Slowo_Boze.pdf"},
    #               recordings={"tenor.wav":"https://drive.google.com/file/d/1nKHHkY50q3uyoShJNviIPex8UXy5HTAL/view?usp=drive_link",
    #                           "Bas.wav":"https://drive.google.com/file/d/1DipBRnOjiDvpTHeQBKIb8ZbuPW-PX_dq/view?usp=drive_link",
    #                           "Przykldowe_wykonanie.wav":'https://www.youtube.com/watch?v=AI2hcI3uoO8'},#"Przykladowe wykonanie.mp3":'https://www.youtube.com/watch?v=AI2hcI3uoO8'},
    #                 startnotes="A5 Eb5 C5 C4")
    
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
    
    app = Choirapp()
    app.read_choirs()
    # app.choirs[0].singers.append(Singer("Zuzia","zuzu","zuzu","sopran"))
    # app.choirs[0].conductors.append(Conductor("Mateusz","matdej3459","dejefa"))
    # app.save_choirs()
    gui = QApplication(sys.argv)
    wind=MainWindow(app)
    wind.show()
    sys.exit(gui.exec())