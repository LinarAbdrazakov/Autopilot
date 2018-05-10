import cv2
import json
from time import time

class RoadSignsDetector(object):


    def __init__(self):
        with open("road_signs_info.json", "r") as file:
            data = json.load(file)

            self.names = []
            for name in data:
                self.names.append(name)

            dirs = {}
            self.alpha = {}
            self.l0 = {}
            self.colors = {}
            for name in self.names:
                dirs[name] = data[name]["dir"]
                self.alpha[name] = data[name]["alpha"]
                self.l0[name] = data[name]["l0"]
                self.colors[name] = data[name]["color"]

            self.cascades = {}
            for name in self.names:
                self.cascades[name] = cv2.CascadeClassifier(dirs[name])

        self.detections = []
        self.names_detect = set()
        self.Counter = Counter(self.names)


    def detect(self, image):
        self.image = image
        self.detections = []
        self.names_detect = set()

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        new_names = self.Counter.get_names()
        for name in new_names:
            cascade = self.cascades[name]
            objects = cascade.detectMultiScale(gray_image, 1.3, 5)
            color = self.colors[name]

            for object in objects:
                self.names_detect.add(name)
                distance = self.get_distance(name, object)
                self.detections.append([name, object, color, distance])

            self.Counter.update_time(name)

        self.Counter.update_names_detect(self.names_detect)

    def get_image_with_signs(self, image=None):
        if image is not None:
            result = image.copy()
        else:
            result = self.image.copy()

        for sign in self.detections:
            name, coordinate, color, distance = sign
            x, y, w, h = coordinate
            cv2.rectangle(result, (x, y), (x+w, y+h), color=color)
            cv2.putText(result, name, (x+w, y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)
            cv2.putText(result, str(distance)+" cm.", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)

        return result


    def distance_calibrate(self):
        pass


    def get_distance(self, name, object):
        x, y, w, h = object
        distance = self.alpha[name]/w + self.l0[name]
        return round(distance, 2)



class Counter(object):

    def __init__(self, names):
        self.names = names
        self.names_detect = set()
        self.time_later_search = {}
        for name in names:
            self.time_later_search[name] = 0

    def get_names(self):
        new_names = self.names_detect.copy()
        new = self.get_new(new_names)
        if new is not None:
            new_names.add(new)

        return new_names

    def update_time(self, name):
       self.time_later_search[name] = time()

    def update_names_detect(self, names_detect):
        self.names_detect = names_detect

    def get_new(self, new_names):
        time_min = time()
        new = None
        for name in self.names:
            if name not in new_names:
                if time_min > self.time_later_search[name]:
                    time_min = self.time_later_search[name]
                    new = name

        return new