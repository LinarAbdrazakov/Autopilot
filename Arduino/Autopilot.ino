#include <Servo.h>

#define ACC_PIN A7
#define SERV_PIN 9

Servo servo;

int strToInt(char s){
  if ('0' <= s <= '9') return s - '0';
  return -1;
}

int get_new_pos(){
    while(Serial.available() < 3){}
    int value = 0; 
    for(int j = 0; j < 3; j++){
      char sym = Serial.read();
      value = value * 10 + strToInt(sym);
    }
    return value;
}

float get_info_acc(){
  float value = analogRead(ACC_PIN);
  float voltage = (value/874)*12.6;
  return voltage;
}

void setup() {
  servo.attach(SERV_PIN);
  Serial.begin(9600);
  pinMode(ACC_PIN, OUTPUT);
}

void loop(){
  int angle = get_new_pos();
  servo.write(angle);
  float voltage = get_info_acc();
  Serial.println(voltage); 
}
