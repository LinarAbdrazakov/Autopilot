import cv2
import numpy as np

cap = cv2.VideoCapture(0)
cascade = cv2.CascadeClassifier("Cascades/give_way.xml")

pris = False
alpha = 2234.8175763736576
pix = 0
l0 = -7.94326744058365

ls = []
pixs_ = []


def get_alpha_and_l0(ls, pixs_):
    #if(len(ls) < 2):
    #   acxept Exception("Small size ls!!!")

    delta_ls = []
    delta_pixs_ = []

    for i in range(len(ls)):
        for j in range(i+1, len(ls)):
            if(ls[i] - ls[j] != 0 and pixs_[i] - pixs_[j] != 0):
                delta_ls.append(ls[i] - ls[j])
                delta_pixs_.append(pixs_[i] - pixs_[j])

    delta_ls_np = np.array(delta_ls)
    delta_pixs_np = np.array(delta_pixs_)
    alphas_np = delta_ls_np/delta_pixs_np
    alpha = np.mean(alphas_np)

    ls0 = np.array(ls) - alpha * np.array(pixs_)
    l0 = np.mean(ls0)

    return alpha, l0


while True:
    _, image = cap.read()

    n_resized = 2
    image = cv2.resize(image, (image.shape[1] // n_resized, image.shape[0] // n_resized), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    objects = cascade.detectMultiScale(gray, 1.3, 5)

    for object in objects:
        x, y, w, h = object
        pix = w
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 255))
        cv2.putText(image, "Object", (x+w, y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
        if pris:
            distance = alpha/pix + l0
            print('Distance: ' + str(distance))
            cv2.putText(image, str(round(distance, 2))+' cm.', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.imshow("Camera", image)
    k = cv2.waitKey(1)

    if k == ord('q'): break

    elif k == ord('s'):
        l = int(input('Input distance to road sign: '))
        ls.append(l)
        pixs_.append(1/float(pix))
        print('Size : ' + str(len(ls)))

    elif k == ord('e'):
        alpha, l0 = get_alpha_and_l0(ls, pixs_)
        print('Alpha for sign: ' + str(alpha))
        print('L0: ' + str(l0))
        pris = True

    elif k == ord('p'):
        pris = True