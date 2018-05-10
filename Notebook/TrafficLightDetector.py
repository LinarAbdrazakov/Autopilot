"""
Программа для детектирования светофора.
Autor: Abdrazakov Linar
Готова к работе!!!
"""
import cv2
import numpy as np
from keras.models import model_from_json
from time import time


class TrafficLightDetector(object):
    """
    Этот класс предназначен для обнаружения светофора на изображении
    и распознавания его цвета.
    Вход: изображение.
    Выход: координаты светофора, его цвет и изображение на котором он выделен.
    """
    def __init__(self):
        self.cascade = cv2.CascadeClassifier('Cascades/traffic_light.xml')
        self.classificator = TrafficLightClassificator()
        self.convert_color = {"red": (0, 0, 255), "yellow": (0, 255, 255), "green": (0, 255, 0)}
        self.alpha = 2234.8175763736576
        self.l0 = -7.94326744058365

        self.detection = []

    def detect(self, image):
        self.result = image.copy()
        self.detection = []
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        signs = self.cascade.detectMultiScale(gray_image, 1.1, 5)
        for (x, y, w, h) in signs:
            roi = image[y:(y+h), x:(x+w)]
            str_color = self.classificator.get_color(roi)
            if str_color is not None:
                color = self.convert_color[str_color]
                distance = self.get_distance((x, y, w, h))
                self.detection.append(["TrafficLight", (x, y, w, h), str_color, color, distance])
                cv2.rectangle(self.result, (x, y), (x+w, y+h), color, 2)
                cv2.putText(self.result, str_color, (x+w, y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)
                cv2.putText(self.result, str(distance)+" cm.", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)

        return self.result

    def get_distance(self, object):
        x, y, w, h = object
        distance = self.alpha/w + self.l0

        return round(distance, 2)



class TrafficLightClassificator(object):
    """
    Этот класс предназначен для определения цвета светофора, а также для проверки на него.
    Вход: изображение светофора.
    Выход: его цвет или отсутствие.
    """

    def __init__(self):
        with open("Model/traffic_light_model.json", "r") as file:
            self.model = model_from_json(file.read())

        self.model.load_weights("Model/traffic_light_model.h5")
        self.model.compile(loss="categorical_crossentropy", optimizer="SGD", metrics=["accuracy"])
        self.codes = {0: None, 1: "red", 2: "yellow", 3: "green"}


    def get_color(self, roi):
        self.roi = roi.copy()
        self.roi = cv2.resize(self.roi, (28, 60), interpolation=cv2.INTER_AREA)

        gray_roi = cv2.cvtColor(self.roi, cv2.COLOR_BGR2GRAY)
        input = np.array(gray_roi).reshape(1, 1680)
        pred = np.argmax(self.model.predict(input))

        return self.codes[pred]


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    detector = TrafficLightDetector()
    count = 0
    start = time()
    while True:
        _, image = cap.read()

        image = cv2.resize(image, (image.shape[1]//2, image.shape[0]//2), interpolation=cv2.INTER_AREA)
        count += 1
        result = detector.detect(image)
        cv2.imshow("Image", result)
        k = cv2.waitKey(1)
        if k == (ord('q') & 0xFF): break
        if(time() - start >= 5):
            print("FPS: ", count/(time() - start))
            count = 0
            start = time()