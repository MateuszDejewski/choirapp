from pathlib import Path
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, 
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, 
    QPushButton, QCheckBox, QRadioButton,
    QListWidget, QListWidgetItem,
    QScrollArea,QSlider
)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QImage,QPixmap
from choir import Choir
from questionnaire import Questionnaire
from score import Score
from song import Song
import fitz
from functools import partial

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
        detaillayout.addWidget(QLabel(self.song.name),0,0,1,2)
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
    def __init__(self,choir:Choir) -> None:
        super().__init__()
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
        self.detailWidget.show()

class QuestionnaireWidget(QWidget):
    def __init__(self, questionnaire: Questionnaire):
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
        



class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Muzyczna Aplikacja")
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        
        self.song_list_widget = SongListWidget()
        layout.addWidget(self.song_list_widget)
        
        self.setLayout(layout)

if __name__=='__main__':
    choir=Choir("karmel")
    choir.addSong(name="Chwała Tobie Królu Wieków",
                  notes={"Chwała Tobie Królu Wieków.pdf":"C:/moje_prace/schola/nuty/Chwala_Tobie_Slowo_Boze.pdf"},
                  recordings={"tenor.wav":"https://drive.google.com/file/d/1nKHHkY50q3uyoShJNviIPex8UXy5HTAL/view?usp=drive_link",
                              "Bas.wav":"https://drive.google.com/file/d/1DipBRnOjiDvpTHeQBKIb8ZbuPW-PX_dq/view?usp=drive_link",
                              "Przykldowe_wykonanie.wav":'https://www.youtube.com/watch?v=AI2hcI3uoO8'},#"Przykladowe wykonanie.mp3":'https://www.youtube.com/watch?v=AI2hcI3uoO8'},
                    startnotes="A5 Eb5 C5 C4")
    
    choir.addSong("Deus miserere mei",
                  notes={"Deus miserere mei.pdf":"https://drive.google.com/file/d/1h6V1yRi1uSyMP1YHK5n8fcsl5mlljqq0/view?usp=drive_link"},
                  recordings={
                      "Sopran.acc":"https://drive.google.com/file/d/1g9FEs0OxgxZZUwo5x0sk23FiwIyXnDZ0/view?usp=drive_link",
                      "Alt.acc":"https://drive.google.com/file/d/1BzCMb9iEYrNv10ERbw9X02PVvHjnD5RW/view?usp=sharing",
                      "Tenor.acc":"https://drive.google.com/file/d/1Cs7y40SvwXcz82mxaBpp8CPBK847IHEC/view?usp=drive_link",
                      "Bas.acc":"https://drive.google.com/file/d/1thVVlh2VCG6eebwNyCUdWFJSNVYwWTfX/view?usp=drive_link"
                  })   
    choir.addSong("Gaude Mater Polonia",
                  notes={"Gaude Mater Polonia.pdf":"https://drive.google.com/file/d/1xy2Z2af-N1hMCYRuzwvIEPWzvIuwm-xO/view?usp=drive_link"},
                  recordings={
                      "Sopran.mp3":"https://drive.google.com/file/d/1zDzagXS1ml6RViRIAxQKjU2z0S05kCIV/view?usp=drive_link",
                      "Alt.mp3": "https://drive.google.com/file/d/1pQMvL4acGuUpOjMQjOkpR_1ys98LhOAc/view?usp=drive_link",
                      "Tenor.mp3": "https://drive.google.com/file/d/1lTL_n4SHS_VXXUOn5cpT7btmFO6W9lfk/view?usp=drive_link",
                      "Bas.mp3":"https://drive.google.com/file/d/1l1K79I9jCQb7yeloApeQfRgwdtumy2Eq/view?usp=drive_link"
                  }
    )
    app = QApplication(sys.argv)
    wind=SongListWidget(choir=choir)
    wind.show()
    sys.exit(app.exec())