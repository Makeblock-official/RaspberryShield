#include <Makeblock.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include "I2Cdev.h"

MeServo servo3(PORT_2,DEV1);//can ONLY be PORT_1,PORT_2
MeServo servoC(PORT_2,DEV2);
MeServo servo4(PORT_1,DEV1);//can ONLY be PORT_1,PORT_2
MeServo servoD(PORT_1,DEV2);

#define IN 0
#define OUT 1
#define POSA 0
#define POS0 1
#define POS1 2

int serparmC[2]={80,35};
int serparmD[2]={85,42};
int serparm3[3]={1,95,180};
int serparm4[3]={1,92,180};

void moveServo(char ser, int pos){
  if(pos>2) return;
  if(ser=='C'){
    servoC.write(serparmC[pos]);
  }else if(ser=='D'){
    servoD.write(serparmD[pos]);  
  }else if(ser=='3'){
    servo3.write(serparm3[pos]);    
  }else if(ser=='4'){
    servo4.write(serparm4[pos]);  
  }
}

void parseCmd(char * cmd){
  char a;
  int b;
  sscanf(cmd,"%c,%d\n",&a,&b);
  Serial.printf(">> %c,%d\n",a,b);
  if(a=='C' || a=='D' || a=='3' || a=='4'){
    // send to sub controller
    moveServo(a,b);
  }
}
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial1.begin(9600); // communicat with main controller
  servo3.begin();
  servo4.begin();
  servoC.begin();
  servoD.begin();
  moveServo('C',OUT);
  moveServo('D',OUT);
  moveServo('3',POS0);
  moveServo('4',POS0);
}

char cmdbuf[64];
int cmdindex;
char dbgbuf[64];
int dbgindex;
void loop() {
  if(Serial1.available()){
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
