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
    QToolBar,QDialogButtonBox
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
from functools import partial
import keyring

class QuestionnaireWidget(QWidget):
    def __init__(self,questionnaire: Questionnaire,user:User):
        super().__init__()
        self.questionnaire = questionnaire
        self.user=user
        layout = QVBoxLayout()

        # Question label
        self.question_label = QLabel(self.questionnaire.question)
        layout.addWidget(self.question_label)

        # Answer widgets
        self.answer_widgets = []
        if self.questionnaire.multipleChoice:
            for answer in self.questionnaire.possibleAnswers:
                checkbox = QCheckBox(answer)
                if user in questionnaire.answers[answer]:
                    checkbox.setChecked(True)
                self.answer_widgets.append(checkbox)
                layout.addWidget(checkbox)
        else:
            self.answer_group = QVBoxLayout()
            for answer in self.questionnaire.possibleAnswers:
                radiobutton = QRadioButton(answer)
                if user in questionnaire.answers[answer]:
                    radiobutton.setAutoExclusive(False)
                    radiobutton.setChecked(True)
                    radiobutton.setAutoExclusive(True)
                self.answer_widgets.append(radiobutton)
                self.answer_group.addWidget(radiobutton)
            layout.addLayout(self.answer_group)

        # New answer input
        if self.questionnaire.addingNewAnswers:
            self.new_answer_input = QLineEdit()
            layout.addWidget(self.new_answer_input)

        # Submit button
        self.submit_button = QPushButton("Dodaj opowiedź")
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

        self.questionnaire.addUserAnswer(self.user, user_answer)
        try:
            self.user.questionnairesToAnswer.remove(self.questionnaire)
        except:
            pass
        self.user.answerdquestionnaires.append(self.questionnaire)
        for widget in self.answer_widgets:
            if self.questionnaire.multipleChoice:
                widget.setChecked(False)
            else:
                widget.setAutoExclusive(False)
                widget.setChecked(False)
                widget.setAutoExclusive(True)

class QuestionnaireManagementWidget(QWidget):
    def __init__(self, mainwindow:MainWindow):
        super().__init__()
        self.mainwindow=mainwindow
        self.user = mainwindow.user
        self.questionnaires = mainwindow.choir.qusetionnaires

        self.setWindowTitle("Zarządzanie ankietami")

        layout = QVBoxLayout()

        # User's questionnaires
        if isinstance(self.user,Singer):
            self.opened_questionnaire=None
            self.user_questionnaires_label = QLabel(f"Ankiety użytkownika {self.user.name}")
            layout.addWidget(self.user_questionnaires_label)

            self.refreshbutton=QPushButton("Odśwież")
            self.refreshbutton.clicked.connect(self.populate_user_questionnaires)
            layout.addWidget(self.refreshbutton)

            self.answered_list = QListWidget()
            self.unanswered_list = QListWidget()

            self.populate_user_questionnaires()

            user_questionnaire_layout = QVBoxLayout()
            user_questionnaire_layout.addWidget(QLabel("Wypełnione"))
            user_questionnaire_layout.addWidget(self.answered_list)
            user_questionnaire_layout.addWidget(QLabel("Niewypełnione"))
            user_questionnaire_layout.addWidget(self.unanswered_list)
            self.answered_list.itemDoubleClicked.connect(self.open_questionnaire)
            self.unanswered_list.itemDoubleClicked.connect(self.open_questionnaire)
            layout.addLayout(user_questionnaire_layout)

        # Conductor's questionnaire management
        if isinstance(self.user, Conductor):
            self.opened_results=None
            self.conductor_questionnaires_label = QLabel("Wszystkie ankiety")
            layout.addWidget(self.conductor_questionnaires_label)

            self.conductor_questionnaire_list = QListWidget()
            self.populate_conductor_questionnaires()
            layout.addWidget(self.conductor_questionnaire_list)
            self.conductor_questionnaire_list.itemDoubleClicked.connect(self.show_results)


            self.add_questionnaire_button = QPushButton("Dodaj ankietę")
            self.add_questionnaire_button.clicked.connect(self.add_questionnaire)
            layout.addWidget(self.add_questionnaire_button)

            self.delete_questionnaire_button = QPushButton("Usuń ankietę")
            self.delete_questionnaire_button.clicked.connect(self.delete_questionnaire)
            layout.addWidget(self.delete_questionnaire_button)

        self.setLayout(layout)

    def populate_user_questionnaires(self):
        self.answered_list.clear()
        self.unanswered_list.clear()
        for q in self.user.answerdquestionnaires:
            item = QListWidgetItem(q.question)
            item.setData(Qt.UserRole, q)
            self.answered_list.addItem(item)
        for q in self.user.questionnairesToAnswer:
            item = QListWidgetItem(q.question)
            item.setData(Qt.UserRole, q)
            self.unanswered_list.addItem(item)
        
        if self.opened_questionnaire:
            self.layout().removeWidget(self.opened_questionnaire)
            self.opened_questionnaire.hide()

    def populate_conductor_questionnaires(self):
        if isinstance(self.user, Conductor):
            self.conductor_questionnaire_list.clear()
            for q in self.questionnaires:
                item = QListWidgetItem(q.question)
                item.setData(Qt.UserRole, q)
                self.conductor_questionnaire_list.addItem(item)

    def add_questionnaire(self):
        dialog = AddQuestionnaireDialog()
        if dialog.exec() == QDialog.Accepted:
            question, possible_answers, adding_new_answers, multiple_choice = dialog.get_questionnaire_data()
            if question:
                new_questionnaire = Questionnaire(question, possibleAnswers=possible_answers,
                                                  addingNewAnswers=adding_new_answers, multipleChoice=multiple_choice)
                self.questionnaires.append(new_questionnaire)
                for singer in self.mainwindow.choir.singers:
                    singer.addQuestionnaire(new_questionnaire)
                self.populate_conductor_questionnaires()


    def delete_questionnaire(self):
        selected_item = self.conductor_questionnaire_list.currentItem()
        if selected_item:
            questionnaire = selected_item.data(Qt.UserRole)
            self.mainwindow.choir.removeQuestionnaire(questionnaire)
            self.populate_conductor_questionnaires()

    def open_questionnaire(self, item):
        questionnaire = item.data(Qt.UserRole)
        if self.opened_questionnaire:
            self.layout().removeWidget(self.opened_questionnaire)
            self.opened_questionnaire.hide()
        self.opened_questionnaire=QuestionnaireWidget(questionnaire, self.user)
        self.layout().addWidget(self.opened_questionnaire)
    

    def show_results(self, item):
        questionnaire = item.data(Qt.UserRole)
        if self.opened_results:
            self.layout().removeWidget(self.opened_results)
            self.opened_results.hide()
        self.opened_results=QuestionnaireResultsWidget(questionnaire)
        self.layout().addWidget(self.opened_results)
        
class AddQuestionnaireDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Questionnaire")
        self.layout = QVBoxLayout()

        # Question input
        self.question_input = QLineEdit()
        self.layout.addWidget(QLabel("Question:"))
        self.layout.addWidget(self.question_input)

        # Answers input
        self.answers_layout = QVBoxLayout()
        self.answers = []
        self.add_answer_button = QPushButton("Add Answer")
        self.add_answer_button.clicked.connect(self.add_answer_field)
        self.layout.addWidget(QLabel("Possible Answers:"))
        self.layout.addLayout(self.answers_layout)
        self.layout.addWidget(self.add_answer_button)

        # Adding new answers option
        self.add_new_answers_checkbox = QCheckBox("Allow Adding New Answers")
        self.layout.addWidget(self.add_new_answers_checkbox)

        # Multiple choice option
        self.multiple_choice_checkbox = QCheckBox("Multiple Choice")
        self.layout.addWidget(self.multiple_choice_checkbox)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def add_answer_field(self):
        answer_input = QLineEdit()
        self.answers_layout.addWidget(answer_input)
        self.answers.append(answer_input)

    def get_questionnaire_data(self):
        question = self.question_input.text()
        possible_answers = [answer.text() for answer in self.answers if answer.text()]
        adding_new_answers = self.add_new_answers_checkbox.isChecked()
        multiple_choice = self.multiple_choice_checkbox.isChecked()
        return question, possible_answers, adding_new_answers, multiple_choice

class QuestionnaireResultsWidget(QWidget):
    def __init__(self, questionnaire: Questionnaire):
        super().__init__()

        layout = QVBoxLayout()

        # Display results
        layout.addWidget(QLabel(questionnaire.question))
        results = questionnaire.getResults()
        for answer, count in results.items():
            layout.addWidget(QLabel(f"{answer}: {count}"))

        for k,v in questionnaire.answers.items():
            userlayout=QHBoxLayout()
            userlayout.addWidget(QLabel(k))
            answers=QLineEdit("")
            answers.setReadOnly(True)
            for user in v:
                answers.setText(answers.text()+user.name+";")

            userlayout.addWidget(answers)
            layout.addLayout(userlayout)

        self.setLayout(layout)
