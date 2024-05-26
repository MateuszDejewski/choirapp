import time
from GUI import MainWindow
from app import Choirapp
from choir import Choir
from performance import Performance
from song import Song
from score import Score
from users import Conductor, Singer
import sys
from PySide6.QtWidgets import QApplication
import pendulum

if __name__=='__main__':
    # choir=Choir("karmel")
    # choir.addSong(name="Chwała Tobie Królu Wieków",
    #               notes={"Chwała Tobie Królu Wieków.pdf":"C:/moje_prace/schola/nuty/Chwala_Tobie_Slowo_Boze.pdf"},
    #               recordings={"tenor.wav":"https://drive.google.com/file/d/1nKHHkY50q3uyoShJNviIPex8UXy5HTAL/view?usp=drive_link",
    #                           "Bas.wav":"https://drive.google.com/file/d/1DipBRnOjiDvpTHeQBKIb8ZbuPW-PX_dq/view?usp=drive_link",
    #                             },
    #                 startnotes="A5 Eb5 C5 C4")
    
    # choir.addSong("Deus miserere mei",
    #               notes={"Deus miserere mei.pdf":"https://drive.google.com/file/d/1h6V1yRi1uSyMP1YHK5n8fcsl5mlljqq0/view?usp=drive_link"},
    #               recordings={
    #                   "Sopran.aac":"https://drive.google.com/file/d/1g9FEs0OxgxZZUwo5x0sk23FiwIyXnDZ0/view?usp=drive_link",
    #                   "Alt.aac":"https://drive.google.com/file/d/1BzCMb9iEYrNv10ERbw9X02PVvHjnD5RW/view?usp=sharing",
    #                   "Tenor.aac":"https://drive.google.com/file/d/1Cs7y40SvwXcz82mxaBpp8CPBK847IHEC/view?usp=drive_link",
    #                   "Bas.aac":"https://drive.google.com/file/d/1thVVlh2VCG6eebwNyCUdWFJSNVYwWTfX/view?usp=drive_link"
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
    # choir.addScore(choir.songs[0],"Będą słowa Chwała Tobie Słowo Boże",-1)
    # choir.addScore(choir.songs[1])
    # choir.performances.append(Performance("Niedziela trójcy świętej",pendulum.DateTime(2024,5,26),songs=choir.scores))
    # app=Choirapp([choir])

    # app.choirs[0].singers.append(Singer("Zuzia","zuzu","zuzu","sopran"))
    # app.choirs[0].conductors.append(Conductor("Mateusz","matdej3459","dejefa"))
    
    # app=Choirapp()
    # app.read_choirs()
    # for song in app.choirs[0].songs:
    #     song.tags=[]
    # app.choirs[0].tagsdict.clear()
    # app.choirs[0].songs.pop()
    # app.save_choirs()


    gui = QApplication(sys.argv)
    wind=MainWindow(Choirapp())
    wind.show()
    sys.exit(gui.exec())