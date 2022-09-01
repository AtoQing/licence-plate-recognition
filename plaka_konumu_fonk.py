import cv2
import matplotlib.pyplot as plt
import numpy as np


def plaka_konum(img):   #img üzerinde çizim yapıp kirletiyor

    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plt.imshow(gray, cmap="gray")
    plt.show()

    # Blur işlemi
    blur = cv2.medianBlur(gray, 5)  # plaka sınır kalınlığı
    blur = cv2.medianBlur(blur, 5)

    plt.imshow(blur, cmap="gray")
    plt.show()

    # Canny için median bulup low, high değerleri çıkardık
    median = np.median(blur)     #median değerinin tutmak için array oluşturduk.
    low = 0.67 * median
    high = 1.33 * median

    canny = cv2.Canny(blur, low, high)

    plt.imshow(canny, cmap="gray")
    plt.show()

    # Canny ile çıkarılan kenarları genişlettik
    dilate = cv2.dilate(canny, np.ones((3, 3), np.uint8), iterations=1)                #iterations çizgi kalınlığı, 3,3 kernel matris ==> 5,5 olursa daha kaın olur.

    plt.imshow(dilate, cmap="gray")
    plt.show()

    cnt = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.RETR_TREE = Hiyerarşik yapı. Yani Dışarıdaki counter ebeveyn içerideki küçük counterler çocuk gibi. Plaka bölgesi parent içerideki karakterler child
    # chain aprox simple tüm pikseller yerine köşegenleri aldık. (yakalanan dikdörtgenlerin köşgenlerini)

    cnt = cnt[0]  # findContours() ilk parametre olarak counter tutuyor. Diğer parametre olan hiyerarşik yapıyı kulanmayacaz
    cnt = sorted(cnt, key=cv2.contourArea, reverse=True)
    # çok fazla contour çıkacak sorted ile tüm counterlerden belli kısmı alcaz. key= cv2.contourArea yani counterlerden kapalı şekilleri al.

    H, W = 500, 500
    plaka = None

    for c in cnt:  # cnt de bulunan tüm dörtgenleri tek tek geziyor.
        rect = cv2.minAreaRect(c)  # Bu dörtgenlerin boyut bilgileri alınıyor.
        (x, y), (w, h), r = rect
        # cv2.minAreaRect(c) c'de yakalanan en küçük alanı döndürür. (x,y,w,h,r) döndürür. x,y merkez koordinatları.

        if (w > h and w > h * 2) or (h > w and h > w * 2):  # plakada h,w oranı en az 2
            box = cv2.boxPoints(rect)  # Koordinatlar = (sol üst, sağ üst, sol alt, sağ alt)  [x,y],[x,y], ...
            box = np.int64(box)  # 64 çünkü counter değerleri - değer de olabilir fotonun dışında ise vs

            minx = np.min(box[:, 0])  # [x,y],[x,y],...  old ilk elemanı almak için 0 de. y leri almak için ise 1 de.  ???
            miny = np.min(box[:, 1])

            maxx = np.max(box[:, 0])
            maxy = np.max(box[:, 1])

            muh_plaka = gray[miny:maxy, minx:maxx].copy()
            muh_median = np.median(muh_plaka)

            #muh_plaka bu koşulları geçerse alınıyor. Kosul 2 ve 3 ten sadece biri sağlanmalı çünkü findCounters() bazen h ile w karıştırıyor
            kosul1 = muh_median > 84 and muh_median < 225
            kosul2 = h < 50 and w < 150
            kosul3 = w < 50 and h < 150

            print(f"muhtemel plaka median = {muh_median}  genislik = {w}   yukseklik = {h}")
            # başa f koyunca { } içindeki değişkenleri basar. f yazmazsan herşeyi aynen yazar.

            #plt.figure()
            bulundu = False
            if (kosul1 and (kosul2 or kosul3)):  # Bu özellikleri sağlayan plaka olarak algılanacak

                cv2.drawContours(img, [box], 0, (0, 255, 0), 2)  # Contourleri birleştirerek img üzerine çizim yapar

                plaka = [int(i) for i in [minx, miny, w, h]]   #plaka = [minx, miny, w, h]

                plt.title("Plaka bulundu !")
                plt.imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
                plt.show()
                bulundu = True
                return plaka



            else:
                cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
                #plt.title("Plaka bulunamadı :(")

            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.show()



    return[]