import time
from choir import Choir
from song import Song
from score import Score

if __name__=='__main__':

    chwala=Song("Chwała Tobie Królu Wieków")
    #chwala.addnotes("C:/moje_prace/schola/nuty/Chwala_Tobie_Slowo_Boze.pdf",)
    #chwala.addrecording("tenor","https://drive.google.com/file/d/1nKHHkY50q3uyoShJNviIPex8UXy5HTAL/view?usp=drive_link",'.wav')
    chwala.addrecording("Przykldowe_wykonanie",'https://youtu.be/bOCuY_M9s90?si=ul9uLMUjLqkdgEEc')
    #chwala.playrecording("tenor.wav")
    
    panie=Song("Panie nie jestem godzien",startnotes="A5 Eb5 C5 C4")
    panie.addrecording("calosc",'https://www.youtube.com/watch?v=bOCuY_M9s90','.wav')
    panie.playrecording("calosc.wav")
    #input("end")
    #time.sleep(40)
    #panie.playStartNotes()
    
    #print("s")
    # sc=Score(panie,transposition=4)
    # sc.playStartNotes()
    # sc.questionare.adduseranswer('u1',"Tak, czuje się w niej pewnie")
    # print(sc.questionare.getresults())

