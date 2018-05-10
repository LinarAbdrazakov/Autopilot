# Класс для приема изображения с камеры машинки
# через Wi-Fi
# Готова к работе!!!
import io
import socket
import numpy as np
import cv2
from PIL import Image
import struct
import time

class VideoStream(object):

    def __init__(self):
        self.socket = socket.socket()
        self.socket.bind(('', 8013))
        self.socket.listen(1)
        self.connection = self.socket.accept()[0].makefile('rb')
        print("Connect succes!")
        self.image = None

    def get_image(self):
        while True:
            image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
            if not image_len:
                break
            image_stream = io.BytesIO()
            image_stream.write(self.connection.read(image_len))
            image_stream.seek(0)
            image = Image.open(image_stream)
            image = np.array(image)
            self.image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            time.sleep(0.01)

    def close(self):
        self.connection.close()
        self.socket.close()