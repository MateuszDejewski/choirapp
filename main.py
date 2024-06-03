import os
from GUI.GUI import MainWindow
from src.app import Choirapp
import sys
from PySide6.QtWidgets import QApplication
from src.choir import Choir
from src.users import Conductor, Singer
if __name__=='__main__':
    # choir=Choir("karmel")
    # choir.addSong(name="Chwała Tobie Królu Wieków",
    #               notes={"Chwała Tobie Królu Wieków.pdf":"C:/moje_prace/schola/nuty/Chwala_Tobie_Slowo_Boze.pdf"},
    #               recordings={"tenor.wav":"https://drive.google.com/file/d/1nKHHkY50q3uyoShJNviIPex8UXy5HTAL/view?usp=drive_link",
    #                           "Bas.wav":"https://drive.google.com/file/d/1DipBRnOjiDvpTHeQBKIb8ZbuPW-PX_dq/view?usp=drive_link",
    #                             },
    #             startnotes="A5 Eb5 C5 C4")
    
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
    # choir.addSong("Duch Pański nade mną",
    #               notes={'duch pański.pdf': 'http://www.nuty.religijne.org/galeria/Duch_Panski_nade_mna_(02-02-2016)_922397_1.pdf'},
    #               recordings={'przykladowe.mp3': 'https://www.youtube.com/watch?v=btxYT0YYVZo', 'bas.mp3': 'https://www.youtube.com/watch?v=pQCl3O6_ews'},
    #               startnotes="Bb5 G5 D5 G4"   
    # ) 
    # choir.addSong("Molitwa Jezusowa",
    #               notes={'ModlitwaJezusowa.pdf': 'https://drive.google.com/file/d/1hEsGoKmUZdtuBHXKmfB1wjdw0d6RBaWw/view?usp=drive_link'},
    #               recordings={'Sopran.mp3': 'https://drive.google.com/file/d/1s_X2VlhvprvIC6MJj57Jk7P_tudFj71A/view?usp=drive_link', 'Alt.mp3': 'https://drive.google.com/file/d/1ysBWoDJQf3oNm0WQmyEnwo41IesUeCWr/view?usp=drive_link', 'Tenor1.mp3': 'https://drive.google.com/file/d/1u9o6E3mX_FII8GwxteehjT-x0nNGT5C1/view?usp=drive_link', 'Tenor2.mp3': 'https://drive.google.com/file/d/1QZ2zxDHwsCk33JOAadRsvMZUxDvTeGa3/view?usp=drive_link', 'Bas.mp3': 'https://drive.google.com/file/d/1JtrX2M_kKmi5YIuJ1vHh7rdDarMj37CI/view?usp=drive_link'},
                   
    # )
    # choir.songs.pop()
    # choir.addSong("Maryjo, prześliczna Pani",
    #                 notes={'nuty.pdf': "C:\\Users\\mateu\\Downloads\\Maryjo prześliczna Pani - Gałuszka.pdf"},
    #                 recordings={'przykladowe wykonanie.mp3': 'https://www.youtube.com/watch?v=8DbtEKKBCT0', 'Sopran.mp3': 'https://www.youtube.com/watch?v=GE6T91IrrE8', 'alt.mp3': 'https://www.youtube.com/watch?v=-gI4JTx4FbU', 'tenor.mp3': 'https://www.youtube.com/watch?v=N7zCcBwKgoE'},  
    # ) 
    # choir.addScore(choir.songs[0],"Będą słowa Chwała Tobie Słowo Boże",-1)
    # choir.addScore(choir.songs[1])
    # #choir.performances.append(Performance("Niedziela trójcy świętej",pendulum.DateTime(2024,5,26),songs=choir.scores))
    # app=Choirapp([choir])

    # app.choirs[0].singers.append(Singer("a","a","a","sopran"))
    # app.choirs[0].conductors.append(Conductor("m","m","m")) 
    
    # app=Choirapp()
    # app.read_choirs()    
    
    # app.save_choirs()

    gui = QApplication(sys.argv)
    wind=MainWindow(Choirapp())
    wind.show()
    sys.exit(gui.exec())