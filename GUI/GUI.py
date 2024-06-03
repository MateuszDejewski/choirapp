import shutil
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QGridLayout,QFormLayout,
    QLabel, QLineEdit, 
    QPushButton,
    QListWidget, QListWidgetItem,
    QComboBox,
    QMessageBox,
    QToolBar
)
from PySide6.QtGui import QAction
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from src.choir import Choir
from src.users import User,Singer,Conductor
from src.app import Choirapp
import keyring

from GUI.GUI_quest import QuestionnaireManagementWidget
from GUI.GUI_songs import SongListWidget
from GUI.GUI_scores import ScorelistWidget
from GUI.GUI_performance import PerformancelistWidget

class MainWindow(QMainWindow):
    def __init__(self,choirapp:Choirapp):
        super().__init__()
        self.downloading=None
        self.setWindowTitle("Aplikacja chóralna")
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

    def setCentralWidget(self,widget):
        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout2 = QHBoxLayout()
        layout2.addLayout(layout)
        central_widget = QWidget()
        central_widget.setLayout(layout2)
        super().setCentralWidget(central_widget)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    
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
        
        #Questionnare list
        quest_list_action = QAction("Wyświetl ankiety", self)
        quest_list_action.triggered.connect(self.change_to_questlist)
        self.toolbar.addAction(quest_list_action)

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
        if len(self.song_list_widget.listofsongs)>0:
            self.setCentralWidget(self.song_list_widget)

    def change_to_scorelist(self):
        if isinstance(self.user,Singer):
            scorelist=self.choir.getScoresForSinger(self.user)
            self.score_list_widget=ScorelistWidget(self,scorelist if scorelist else [])
        else:
            self.score_list_widget=ScorelistWidget(self,self.choir.scores)
        if len(self.score_list_widget.listofsongs)>0:
            self.setCentralWidget(self.score_list_widget)

    def change_to_performancelist(self):
        if isinstance(self.user,Singer):
            perflist=self.choir.getPerformancesForSinger(self.user)
            self.performance_list_widget=PerformancelistWidget(self,perflist if perflist else [])
        else:
            self.performance_list_widget=PerformancelistWidget(self,self.choir.performances)
        if len(self.performance_list_widget.performances)>0:
            self.setCentralWidget(self.performance_list_widget)

    def change_to_questlist(self):
        self.questmanagement=QuestionnaireManagementWidget(self)
        self.setCentralWidget(self.questmanagement)

    def change_to_managechoir(self):
        self.choirmanagement=ChoirmanegementWidget(self)
        self.setCentralWidget(self.choirmanagement)

    def change_to_account(self):
        self.accountwidget = UserdataWidget(self, self.user)
        self.setCentralWidget(self.accountwidget)

    def logout(self):
        self.user = None
        self.choir = None
        self.logwidget = LoginWindow(self)
        self.logwidget.setMaximumSize(300,200)
        self.setCentralWidget(self.logwidget)
        self.toolbar.setVisible(False)

class MenuWidget(QWidget):
    def __init__(self,mainWindow:MainWindow) -> None:
        super().__init__()
        self.mainwindow=mainWindow
        self.user=self.mainwindow.user
        
        self.mainwindow.login_successful()

        menulayout=QVBoxLayout()
        
        namelabel=QLabel("Jesteś zalogowany jako "+self.user.name)
        namelabel.setAlignment(Qt.AlignCenter)
        font = namelabel.font()
        font.setPointSize(15)
        namelabel.setFont(font)
        menulayout.addWidget(namelabel)


        self.songlistbutton=QPushButton("Wyświetl listę utworów")
        self.songlistbutton.clicked.connect(self.change_to_songlist)
        menulayout.addWidget(self.songlistbutton)

        self.scorelistbutton=QPushButton("Wyświetl listę pieśni do nauki")
        self.scorelistbutton.clicked.connect(self.change_to_scorelist)
        menulayout.addWidget(self.scorelistbutton)

        self.performancelistbutton=QPushButton("Wyświetl listę występów")
        self.performancelistbutton.clicked.connect(self.change_to_performancelist)
        menulayout.addWidget(self.performancelistbutton)

        self.questlistbutton=QPushButton("Wyświetl listę ankiet")
        self.questlistbutton.clicked.connect(self.change_to_questlist)
        menulayout.addWidget(self.questlistbutton)

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
        if len(self.song_list_widget.listofsongs)>0:
            self.mainwindow.setCentralWidget(self.song_list_widget)

    def change_to_scorelist(self):
        if isinstance(self.user,Singer):
            scorelist=self.mainwindow.choir.getScoresForSinger(self.user)
            self.score_list_widget=ScorelistWidget(self.mainwindow,scorelist if scorelist else [])
        else:
            self.score_list_widget=ScorelistWidget(self.mainwindow,self.mainwindow.choir.scores)
        if len(self.score_list_widget.listofsongs)>0:
            self.mainwindow.setCentralWidget(self.score_list_widget)

    def change_to_performancelist(self):
        if isinstance(self.user,Singer):
            perflist=self.mainwindow.choir.getPerformancesForSinger(self.user)
            self.performance_list_widget=PerformancelistWidget(self.mainwindow,perflist if perflist else [])
        else:
            self.performance_list_widget=PerformancelistWidget(self.mainwindow,self.mainwindow.choir.performances)
        if len(self.performance_list_widget.performances)>0:
            self.mainwindow.setCentralWidget(self.performance_list_widget)

    def change_to_questlist(self):
        self.questmanagement=QuestionnaireManagementWidget(self.mainwindow)
        self.mainwindow.setCentralWidget(self.questmanagement)

    def change_to_managechoir(self):
        self.choirmanagement=ChoirmanegementWidget(self.mainwindow)
        self.mainwindow.setCentralWidget(self.choirmanagement)

    def change_to_account(self):
        self.accountwidget=UserdataWidget(self.mainwindow,self.user)
        self.mainwindow.setCentralWidget(self.accountwidget)

    def logout(self):
        self.logwidget=LoginWindow(self.mainwindow)
        self.logwidget.setMaximumSize(300,200)
        self.mainwindow.setCentralWidget(self.logwidget)

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

        self.savebutton=QPushButton("Wyczycść dane zapisane na komputerze")
        self.savebutton.clicked.connect(self.removefiles)
        layout.addWidget(self.savebutton,6,0,1,2)

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

    def removefiles(self):
        self.mainwidnow.choir.removefiles()
        QMessageBox.information(self,"Sukces","Pomyślnie usunięto pliki chóru z tego urządzenia")

class ChoirmanegementWidget(QWidget):
    def __init__(self, mainwindow:MainWindow):
        super().__init__()
        self.mainwindow=mainwindow
        self.setWindowTitle("Choir Management")
        self.choir = self.mainwindow.choir
        self.conductors = self.choir.conductors
        self.singers = self.choir.singers
        self.selected_member = None

        main_layout = QVBoxLayout()

        
        self.choir_name_label = QLabel(f"Chór: {self.choir.name}")
        self.choir_name_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.choir_name_label)
        self.delete_choir_button = QPushButton("Usuń chór")
        self.delete_choir_button.clicked.connect(self.delete_choir)
        main_layout.addWidget(self.delete_choir_button)

        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("Lista dyrygentów:"))
        self.conductor_list = QListWidget()
        self.conductor_list.setSelectionMode(QListWidget.SingleSelection)
        self.conductor_list.itemClicked.connect(self.display_member_details)
        list_layout.addWidget(self.conductor_list)

        list_layout.addWidget(QLabel("Lista chórzystów:"))
        self.singer_list = QListWidget()
        self.singer_list.setSelectionMode(QListWidget.SingleSelection)
        self.singer_list.sortItems()
        self.singer_list.itemClicked.connect(self.display_member_details)
        list_layout.addWidget(self.singer_list)

        main_layout.addLayout(list_layout)

        # Populate the lists with conductors and singers
        self.populate_member_lists()

        detail_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        detail_layout.addRow("Nazwa użytkownika:", self.name_edit)

        self.login_edit = QLineEdit()
        detail_layout.addRow("Login:", self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        detail_layout.addRow("Hasło:", self.password_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Chórzysta","Dyrygent"])
        self.role_combo.currentTextChanged.connect(self.role_changed)
        detail_layout.addRow("Rola",self.role_combo)

        self.voice_edit = QLineEdit()
        detail_layout.addRow("Podatawowy głos:", self.voice_edit)

        self.save_button = QPushButton("Zapisz zmiany")
        self.save_button.clicked.connect(self.save_member_details)
        self.add_button = QPushButton("Dodaj użytkownika")
        self.add_button.clicked.connect(self.save_member_details)
        self.delete_button = QPushButton("Usuń użytkownika")
        self.delete_button.clicked.connect(self.delete_member)
        self.clear_button = QPushButton("Wyczyść pola")
        self.clear_button.clicked.connect(self.clear_detail_fields)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        

        detail_layout.addRow(button_layout)

        main_layout.addLayout(detail_layout)

        self.setLayout(main_layout)

    def populate_member_lists(self):
        self.conductor_list.clear()
        self.singer_list.clear()
        for conductor in self.conductors:
            item = QListWidgetItem(conductor.name)
            item.setData(Qt.UserRole, conductor)
            self.conductor_list.addItem(item)
        for singer in self.singers:
            item = QListWidgetItem(singer.name)
            item.setData(Qt.UserRole, singer)
            self.singer_list.addItem(item)
        self.conductor_list.sortItems()
        self.singer_list.sortItems()

    def display_member_details(self, item):
        member = item.data(Qt.UserRole)
        self.selected_member = member
        self.name_edit.setText(member.name)
        self.login_edit.setText(member.login)
        self.password_edit.setText(keyring.get_password("app", member.login))
        if isinstance(member, Conductor):
            self.role_combo.setCurrentText("Dyrygent")
            self.voice_edit.clear()
            self.voice_edit.setEnabled(False)
        else:
            self.role_combo.setCurrentText("Chórzysta")
            self.voice_edit.setText(member.basicvoice)
            self.voice_edit.setEnabled(True)

    def save_member_details(self):
        def changebasics():
            name=self.name_edit.text()
            login=self.login_edit.text()
            password=self.password_edit.text()
            if self.selected_member.name!=name:
                self.selected_member.name = name
            if self.selected_member.login!=login:
                self.selected_member.changelogin()
            self.selected_member.changepassword(password)

        if self.selected_member:
            if isinstance(self.selected_member,Conductor):
                if self.role_combo.currentText()=="Dyrygent":
                    changebasics()
                elif self.role_combo.currentText()=="Chórzysta":
                    oldmember=self.selected_member
                    self.selected_member=None
                    self.save_member_details()
                    self.selected_member=oldmember
                    self.delete_member()
            if isinstance(self.selected_member,Singer):
                if self.role_combo.currentText()=="Chórzysta":
                    changebasics()
                    self.selected_member.basicvoice=self.voice_edit.text()
                elif self.role_combo.currentText()=="Dyrygent":
                    oldmember=self.selected_member
                    self.selected_member=None
                    self.save_member_details()
                    self.selected_member=oldmember
                    self.delete_member()
        else:
            name = self.name_edit.text()
            login = self.login_edit.text()
            password = self.password_edit.text()
            role = self.role_combo.currentText()
            if role == "Dyrygent":
                new_member = Conductor(name, login, password)
                self.conductors.append(new_member)
            else:
                basicvoice = self.voice_edit.text()
                new_member = Singer(name, login, password, basicvoice)
                for quest in self.choir.qusetionnaires:
                    new_member.addQuestionnaire(quest)
                self.singers.append(new_member)
            self.clear_detail_fields()
        self.populate_member_lists()
            
        
    def delete_member(self):
        if self.selected_member:
            if isinstance(self.selected_member, Conductor):
                self.conductors.remove(self.selected_member)
            else:
                self.singers.remove(self.selected_member)
            self.selected_member.deletepassword()
            self.clear_detail_fields()

    def clear_detail_fields(self):
        self.selected_member = None
        self.name_edit.clear()
        self.login_edit.clear()
        self.password_edit.clear()
        self.role_combo.setCurrentText("")
        self.voice_edit.clear()
        self.populate_member_lists()

    def role_changed(self, role):
        if role == "Dyrygent":
            self.voice_edit.clear()
            self.voice_edit.setEnabled(False)
        else:
            self.voice_edit.setEnabled(True)

    def delete_choir(self):
        answer=QMessageBox.question(self,"Usuwanie chóru","Czy na pewno chcesz usunąć chór?\nWszystkie dane zostaną bezpowrotnie utracone",
                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer==QMessageBox.Yes:
            self.mainwindow.choirapp.delete_choir(self.choir)
            self.mainwindow.setCentralWidget(LoginWindow(self.mainwindow))