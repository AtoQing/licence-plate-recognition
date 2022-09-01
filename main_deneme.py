from PyQt5.QtWidgets import *       #gui için temel iki kütüphane
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap   #pixmap GUI ye foto koymak için
import sqlite3 as sql

import cv2
from plaka_okuma_fonk import plaka_okuma
from karakter_tanima_fonk import karakter_tanima
import datetime
from datetime import datetime

import os
import time
from pymata4 import pymata4


adres = 'C:\\Users\Admin\Desktop\plaka\\12.jpg'

img = cv2.imread(adres)
img_clear = cv2.imread(adres)         #contour çizilmemiş temiz resim
img = cv2.resize(img, (500, 500))
img_clear = cv2.resize(img_clear, (500, 500))

conn = sql.connect("otopark.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS ARACLAR(
    Plaka BLOB,
    Giris_Saati text,
    Cikis_Saati text)""")


#plaka resmini binary code yaptık database için
#jpeg_bytes = open(options.plate_image, "rb").read()    buna benzer dene
with open("plaka.jpg", "rb") as file:
    plaka_code = file.read()



class main(QMainWindow):   #tüm gui ve kodlar burda olmalı. self vs def dışında çalışmaz.
    def __init__(self):
        super().__init__()
        loadUi("tasarim.ui", self)

        plaka_okuma(img, img_clear)
        karakter_tanima()
        karakterler = os.listdir("plaka karakterleri")

        green_led = 10
        trigpin = 11
        ecopin = 12
        red_led = 9


        board = pymata4.Pymata4()
        board.set_pin_mode_digital_output(red_led)
        board.set_pin_mode_digital_output(green_led)


        if len(karakterler)!=0:             # karakterler klasörü boş değilse yani araç plakası alınmışsa süreyi başlat 
            Giriş = datetime.now()
            saat = datetime.strftime(Giriş, '%X')
            tarih = str(Giriş.day) + "/" + str(Giriş.month) + "/" + str(Giriş.year) + "   " + str(saat)
            self.textBrowser_9.setText(tarih)



        def the_callback(data):
            pass

        # print("distance ", data[2])   # data[2] çünkü data= [echo_pin, trig_pin, distance, ?]

        board.set_pin_mode_sonar(trigpin, ecopin, the_callback)  # 1 ve 2 input. 3. ise çalışırken çağıracağı fonk

        while True:  # if else buraya koyuyor
            try:

                time.sleep(0.1)  #süre uzun olursa genelde hata veriyor. Çünkü python aynı anda iki işi yapamıyor. sleep demek tüm sistemi uyutmak demek
                value = board.sonar_read(trigpin)
                print("VALUE=", value[0])  # value = [distance, ?]


                if value[0] == None:
                    pass

    # yaklaşma durumu
    
                if value[0] < 50:               
                    if len(karakterler) != 0:       # Klasör boş değilse araç gelmiştir

                        board.digital_write(green_led, 1)
                        time.sleep(0.2)
                        print("araç parkta !!")
                        self.textBrowser.setStyleSheet("background-color:red;")

                    if len(karakterler) == 0:       # klasör boş ise cisim gelmiştir

                        board.digital_write(red_led, 1)
                        time.sleep(1)
                        print("Sensorde cisim var !!")


# uzaklaşma durumu

                if value[0] > 50:          
                    
                    if len(karakterler) == 0:           # klasör boş ise cisim uzaklaşmıştır
                        print("cisim ayrildi !!")
                        board.digital_write(red_led, 0)
                        time.sleep(0.2)
                        break

                    if len(karakterler) != 0:            # klasör dolu ise araba uzaklaşmıştır
                        print("arac ayrildi !!")
                        board.digital_write(green_led, 0)
                        time.sleep(0.2)

                        self.pixmap = QPixmap('plaka.jpg')
                        self.label.setPixmap(self.pixmap)           # image label üstüne basılabilir. text vs basmaz
                        Çıkış = datetime.now()
                        saat1 = datetime.strftime(Çıkış, '%X')
                        tarih1 = str(Çıkış.day) + "/" + str(Çıkış.month) + "/" + str(Çıkış.year) + "   " + str(saat1)
                        #print(tarih1)
                        cursor.execute("""INSERT INTO ARACLAR VALUES(?,?,?)""", (plaka_code, tarih, tarih1))
                        self.textBrowser_11.setText(tarih1)

                        board.digital_write(green_led, 0)
                        time.sleep(0.2)
                        board.shutdown()

                        conn.commit()  # Data base kapat
                        conn.close()
                        break

            except Exception:  # kullanmadık üstte break old
                print("System finish...")
                #board.shutdown()
                break

uygulama = QApplication([])   #GUI kapat
pencere = main()
pencere.show()
uygulama.exec_()


