import socket
import serial
import time
import RPi.GPIO as GPIO
from threading import Thread 
import Adafruit_CharLCD as LCD
import subprocess

GPIO.setmode(GPIO.BCM)

class Arduino(object):

    def __init__(self):
        self.port = serial.Serial('/dev/ttyUSB0', 9600)
        self.angle = 90
        self.voltage = None

    def write(self, data):
        self.port.write(data.encode('utf-8'))

    def read(self):
        data = self.read().decode('utf-8')
        return data

    def servo_write(self):
        self.write('0'*(3-len(str(self.angle)))+str(self.angle))

    def get_acc(self):
        text = self.read()
        data = text.split('\n')[-1]
        self.voltage = float(data)
	

class HC_SR04(object):

    def __init__(self):
        self.TRIG = 3
        self.ECHO = 2
        self.distance = None
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

    def get_dist(self):
        while True:
            start = time.time()
            GPIO.output(self.TRIG, True)
            time.sleep(0.00001)
            GPIO.output(self.TRIG, False)
            while GPIO.input(self.ECHO) == False:
                pass
            start = time.time()
            while GPIO.input(self.ECHO) == True:
                pass
            stop = time.time()
            self.distance = (stop - start) * 17000
            time.sleep(max(0.1 - (time.time() - start), 0))

class ServerComunicate(object):

    def __init__(self):
        self.socket = socket.socket()
        self.socket.connect(('0.0.0.0', 9000))

        self.road_signs = []
        self.traffic_signs = [] 	
        self.name_signs = ['Stop', 'Main Road', 'One Way', 'Give Way', 'No Entry']
        self.road = None
        self.curvature = None
        self.pos = None

    def comunicate(self):
        data = self.socket.recv(1024).encode('utf-8').split()
        self.road_signs = []
        self.traffic_signs = []
        i = 0
        while i < len(data):
            if data[i] == "traffic_sign":
                self.traffic_signs.append([data[i].replace('_', ' '), data[i+1], int(data[i+2])]) # 0:name, 1:color, 2:distance 
                i += 3
            elif (data[i].replace('_',  ' ')) in self.name_signs:
                self.road_sign.append([data[i].replace('_', ' '), int(data[i+1])]) # 0:name, 1:distance
                i += 2
            elif data[i] == "info_road":
                self.road = data[i+1]
                self.curavture = float(data[i+2])
                self.pos = float(data[i+3])
                i += 4

    def close(self):
        self.socket.close()

class Motor(object):

    def __init__(self):
        self.SpeedPin1 = 21 
        self.ForwardPin1 = 16
        self.AgoPin1 = 20
        self.SpeedPin2 = 13
        self.ForwardPin2 = 26
        self.AgoPin2 = 19
        GPIO.setup(self.SpeedPin1, GPIO.OUT)
        GPIO.setup(self.ForwardPin1, GPIO.OUT)
        GPIO.setup(self.AgoPin1, GPIO.OUT)
        GPIO.setup(self.SpeedPin2, GPIO.OUT)
        GPIO.setup(self.ForwardPin2, GPIO.OUT)
        GPIO.setup(self.AgoPin2, GPIO.OUT)
        self.Speed1 = GPIO.PWM(self.SpeedPin1, 500)
        self.Speed2 = GPIO.PWM(self.SpeedPin2, 500)
        self.Speed2.start(0) 	
        self.Speed1.start(0)

    def go(self, speed):
        GPIO.output(self.ForwardPin1, 1)        
        GPIO.output(self.AgoPin1, 0)
        self.Speed1.ChangeDutyCycle(speed)
        GPIO.output(self.ForwardPin2, 1)
        GPIO.output(self.AgoPin2, 0)
        self.Speed2.ChangeDutyCycle(speed)

    def clean(self):
        self.Speed1.stop()
        self.Speed2.stop()

class Lights(object):
	
    def __init__(self):
        self.MainLightPin = 0
        self.RightPin = 0
        self.LeftPin = 0
        self.StopPin = 0
	  
        GPIO.setup(self.MainLightPin, GPIO.OUT)
        GPIO.setup(self.RightPin, GPIO.OUT)
        GPIO.setup(self.LeftPin, GPIO.OUT)
        GPIO.setup(self.StopPin, GPIO.OUT)

        self.Main = GPIO.PWM(self.MainLightPin, 500)
        self.Right = GPIO.PWM(self.RightPin, 500)
        self.Left = GPIO.PWM(self.LeftPin, 500)
        self.Stop = GPIO.PWM(self.StopPin, 500) 

        self.Main.start(0)
        self.Right.start(0)
        self.Left.start(0)
        self.Stop.start(0)

        self.MainValue = 0
        self.StopValue = 0
        self.delay = 0.005
        self.delay_turn = 0.005

    def main_light(self, value):
        while value > self.MainValue:
            self.MainValue += 1
            self.Main.ChangeDutyCycle(self.MainValue)
            time.sleep(delay)
        while value < self.MainValue:
            self.MainValue -= 1
            self.Main.ChangeDutyCycle(self.MainValue)
            time.sleep(delay)

    def stop_light(self, value):
        while value > self.StopValue:
            self.StopValue += 1
            self.Stop.ChangeDutyCycle(self.StopValue)
            time.sleep(delay)
        while value < self.MainValue:
            self.StopValue -= 1
            self.Stop.ChangeDutyCycle(self.StopValue)
            time.sleep(delay)

    def turn_signal(self, lihts='right&left'):
        for i in range(101):
            if 'right' in lights: self.Right.ChangeDutyCycle(i)
            if 'left' in lights: self.Left.ChangeDutyCycle(i)
            time.sleep(self.delay_turn)
        for i in range(100, -1, -1):
            if 'right' in lights: self.Right.ChangeDutyCycle(i)
            if 'left' in lights: self.Left.ChangeDutyCycle(i)
            time.sleep(self.delay_turn)

class Display(object):

    def __init__(self):
        self.rs = 25
        self.en = 24
        self.d4 = 23
        self.d5 = 17
        self.d6 = 4
        self.d7 = 22
        self.backlight = 4
        self.columns = 16
        self.rows = 2
        
        self.lcd = LCD.Adafruit_CharLCD(self.rs, self.en, self.d4, self.d5, self.d6, self.d7, self.rows, self.columns)
        
        self.lcd.message("Hello, Linar!")
        time.sleep(3)
        self.lcd.clear()
   
    def print_self_ip(self):        
        process = subprocess.Popen(["hostname", "-I"], stdout=subprocess.PIPE)
        text = process.communicate()[0][:-1].decode('utf-8')
        self.lcd.message("Car IP:\n"+text)
        time.sleep(10)
        self.lcd.clear()

class CarState(object):

    def __init__(self):
        self.angle = 90
        self.speed = 0
        self.go = "forward"

        self.sonar_distance = None
        self.road_signs = []
        self.traffic_signs = []

        self.main_light = 0
        self.right_light = "off"
        self.left_light = "off"

def main():
    try:
        #GPIO.setmode(GPIO.BCM)
        #display = Display()
        #display.print_self_ip()
        #Range_sensor = HC_SR04()
        #range_sensor_flow = Thread(target=Range_sensor.get_dist)
        #range_sensor_flow.start()
        motor = Motor()
        arduino = Arduino()
        arduino.servo_write()
        motor.go(50)
        time.sleep(10)
       
    finally:
        motor.clean()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
