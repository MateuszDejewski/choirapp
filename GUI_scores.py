from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget,
)

from GUI_songs import SongListWidget

class ScorelistWidget(SongListWidget):
    def __init__(self, mainwindow:MainWindow, listofsongs:list[Score]|list[Song]) -> None:
        super().__init__(mainwindow,listofsongs)

    def addnewsong(self):
        pass

    def editsong(self):
        pass       




        
