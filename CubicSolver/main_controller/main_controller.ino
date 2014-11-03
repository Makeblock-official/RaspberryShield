#include <Makeblock.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include "I2Cdev.h"

MeServo servo2(PORT_1,DEV1);//can ONLY be PORT_1,PORT_2
MeServo servoB(PORT_1,DEV2);
MeServo servo1(PORT_2,DEV1);//can ONLY be PORT_1,PORT_2
MeServo servoA(PORT_2,DEV2);
SoftwareSerial subtrl(MISO,SCK); // RX, TX, port5

#define IN 0
#define OUT 1
#define POSA 0
#define POS0 1
#define POS1 2

int serparmB[2]={60,22};
int serparmA[2]={70,32};
int serparm2[3]={1,85,172};
int serparm1[3]={1,90,180};

void moveServo(char ser, int pos){
  if(pos>2) return;
  if(ser=='A'){
    servoA.write(serparmA[pos]);
  }else if(ser=='B'){
    servoB.write(serparmB[pos]);  
  }else if(ser=='1'){
    servo1.write(serparm1[pos]);    
  }else if(ser=='2'){
    servo2.write(serparm1[pos]);  
  }
}

void parseCmd(char * cmd){
  char a;
  int b;
  sscanf(cmd,"%c,%d\n",&a,&b);
  Serial.printf(">> %c,%d\n",a,b);
  if(a=='A' || a=='B' || a=='1' || a=='2'){
    moveServo(a,b);
  }else if(a=='C' || a=='D' || a=='3' || a=='4'){
    // send to sub controller
    subtrl.print(cmd);
  }
}

void setup() {
  Serial.begin(9600);
  Serial1.begin(115200);
  subtrl.begin(9600);
  servo1.begin();
  servo2.begin();
  servoA.begin();
  servoB.begin();
  moveServo('A',OUT);
  moveServo('B',OUT);
  moveServo('1',POS0);
  moveServo('2',POS0);
}

char cmdbuf[64];
int cmdindex;
char dbgbuf[64];
int dbgindex;
void loop() {
  if(Serial1.available()){
    // cmd from rasp
    char c = Serial1.read();
    Serial.write(c);
    cmdbuf[cmdindex++]=c;
    if(c=='\n'){
      parseCmd(cmdbuf);
      memset(cmdbuf,0,64);  
      cmdindex=0;
    }

  }
  
  if(Serial.available()){
    char c = Serial.read();
    dbgbuf[dbgindex++]=c;
    if(c=='\n'){
      parseCmd(dbgbuf);
      memset(dbgbuf,0,64);  
      dbgindex=0;
    }
  }
}
