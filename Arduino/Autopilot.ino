#include <Servo.h>

#define ACC_PIN A7
#define SERV_PIN 9

Servo servo;

int strToInt(char s){
  int i = -1;
  if(s == '0'){ i = 0; }
  else if(s == '1'){ i = 1; }
  else if(s == '2'){ i = 2; }
  else if(s == '3'){ i = 3; }
  else if(s == '4'){ i = 4; }
  else if(s == '5'){ i = 5; }
  else if(s == '6'){ i = 6; }
  else if(s == '7'){ i = 7; }
  else if(s == '8'){ i = 8; }
  else if(s == '9'){ i = 9; }
  return i;
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
