import cv2
from RoadSignsDetector import RoadSignsDetector
from TrafficLightDetector import TrafficLightDetector
import numpy as np
from time import time

if __name__ == '__main__':
    RS_Detector = RoadSignsDetector()
    TL_Detector = TrafficLightDetector()

    cap = cv2.VideoCapture(0)

    count = 0
    start = time()

    while True:
        _, image = cap.read()

        image_resized = cv2.resize(image, (image.shape[1]//2, image.shape[0]//2), interpolation=cv2.INTER_AREA)

        RS_Detector.detect(image_resized)
        result = TL_Detector.detect(image_resized)
        result = RS_Detector.get_image_with_signs(result)

        cv2.imshow("Image", result)
        k = cv2.waitKey(1)
        if k == ord('q'): break

        count += 1
        if time() - start >= 5:
            print("FPS: ", round(count/(time() - start), 2))
            count = 0
            start = time()