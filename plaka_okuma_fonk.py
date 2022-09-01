import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pytesseract
from plaka_konumu_fonk import plaka_konum


def plaka_okuma(img,img_clear):


    # Plaka okuma ve Karakterleri Ayrıştırma. Projenin klasöründeki karakterseti klasöründe !!!
    img = cv2.resize(img, (500, 500))              #main denemede resize yaptık zaten
    img_clear = cv2.resize(img_clear, (500, 500))

    plaka = plaka_konum(img)
    x, y, w, h = plaka  # başlangıç noktasının x,y,w,h, değerlerini tutar

    # Find contours algılarken h ve w bazen karıştırabilir. (birkaç arabada çıktılara bak w , h den küçük değer almış). Bu yüzden w ve h kontrol etmek için algoritma kurduk.

    if (w > h):  # olması gereken durum yani w>h ise
        plaka_bgr = img_clear[y:y + h, x:x + w].copy()

    else:  # yanlış algılamış ise yani h>w ise
        plaka_bgr = img_clear[y:y + w, x:x + h].copy()

    cv2.imshow("Plaka", plaka_bgr)
    cv2.waitKey(0)

    cv2.imwrite("plaka.jpg", plaka_bgr)

    H, W = plaka_bgr.shape[:2]
    #plt.imshow(plaka_bgr)
    #plt.show()

    # daha buyuk boyut. Pikseller yok olur.
    H, W = H * 2, W * 2
    plaka_bgr = cv2.resize(plaka_bgr, (W, H))  # plaka genişlettik
    cv2.imshow("Boyutlandirilmis Plaka", plaka_bgr)
    cv2.waitKey(0)

    #plt.imshow(plaka_bgr)
    #plt.show()

    plaka_gray = cv2.cvtColor(plaka_bgr, cv2.COLOR_BGR2GRAY)
    plaka_threshold = cv2.adaptiveThreshold(plaka_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    #Adaptive Threshod = Eşik değeri, o alanın çevresindeki değerlerin ortalamasıyla hesaplanarak bulunur ve işlem uygulanır. Normal thresholdda eşik değerini biz veriyoruz.

    cv2.imshow("Plaka Threshold", plaka_threshold)
    cv2.waitKey(0)

    kernel = np.ones((3, 3), np.uint8)
    plaka_threshold = cv2.morphologyEx(plaka_threshold, cv2.MORPH_OPEN, kernel, iterations=1)
    cv2.imshow("Gurultu yok edilmis", plaka_threshold)
    cv2.waitKey(0)

    cnt = cv2.findContours(plaka_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = cnt[0]  # counterler ilk sırada tutuluyor
    cnt = sorted(cnt, key=cv2.contourArea, reverse=True)[:15]

    for i, c in enumerate(cnt):

        rect = cv2.minAreaRect(c)
        (x, y), (w, h), r = rect

        kosul1 = max([w, h]) < W / 4
        kosul2 = w * h > 200

        if (kosul1 and kosul2):
            print("karakter ==>", x, y, w, h)

            box = cv2.boxPoints(rect)
            box = np.int64(box)

            minx = np.min(box[:, 0])
            miny = np.min(box[:, 1])
            maxx = np.max(box[:, 0])
            maxy = np.max(box[:, 1])

            odak = 2

            minx = max(0, minx - odak)  # harfin solundaki x değeri
            miny = max(0, miny - odak)
            maxx = min(W, maxx + odak)  # harfin sağındaki x değeri
            maxy = min(H, maxy + odak)

            roi = plaka_bgr[miny:maxy, minx:maxx].copy()  # bulunan harf

            try:
                # cv2.imwrite(f"karakterseti/karakter{i}.jpg", roi)

                cv2.imwrite(f"plaka karakterleri/{minx}.jpg", roi)
            # plaka karakterlerini minx adıyla kaydetttik. Böylece klasörde x değeri küçük olan değer başa gelecek ve doğru sıra ile keydedilmiş olcak

            except:
                pass

            yaz = plaka_bgr.copy()
            cv2.drawContours(yaz, [box], 0, (0, 255, 0), 1)

            plt.imshow(yaz)
            plt.show()




"""
    #OKUMA DENEME
    img= cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img = cv2.bilateralFilter(img, 11,17,17)
    cv2.imshow("bilateral", img)
    (_, img) = cv2.threshold(img, 150,180, cv2.THRESH_BINARY)
    cv2.imshow("threshold", img)
    cv2.waitKey(0)
    text= pytesseract.image_to_string(img, lang= "eng")
    print("detected text:", text)
    """




