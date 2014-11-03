#include <SoftwareSerial.h>
#include <Wire.h>
#include <String.h>
#include <OneWire.h>
#include "Servo.h"

#define NC -1
#define NUM_QUERYLIST 10

#define SLOT1 0
#define SLOT2 1

#define PORT_1 				0x01
#define PORT_2 				0x02
#define PORT_3 				0x03
#define PORT_4 				0x04
#define PORT_5 				0x05
#define PORT_6 				0x06
#define PORT_7 				0x07
#define PORT_8 				0x08
#define M1     				0x09
#define M2     				0x0a

#define NOP __asm__("nop\n\t")
#define HIGH0 *P_RGB = PINON;*P_RGB = PINOFF;
#define HIGH1 *P_RGB = PINON;NOP;NOP;NOP;NOP;*P_RGB = PINOFF;

#define buzzerOn()  DDRE |= 0x04,PORTE |= B00000100
#define buzzerOff() DDRE |= 0x04,PORTE &= B11111011

#if defined(__AVR_ATmega32U4__) //MeBaseBoard use ATmega32U4 as MCU
unsigned char mePort[11][2] = {{NC, NC}, {11, A8}, {13, A11}, {A10, A9}, {1, 0},
    {MISO, SCK}, {A0, A1}, {A2, A3}, {A4, A5}, {6, 7}, {5, 4}
};
#else // else ATmega328
unsigned char mePort[11][2] = {{NC, NC}, {11, 10}, {3, 9}, {12, 13}, {8, 2},
    {NC, NC}, {A2, A3}, {NC, A1}, {NC, A0}, {6, 7}, {5, 4}
};
#endif

Servo servox,servoy;

void doDcRun(char port, int speed)
{
  char dpin,apin;
  dpin = mePort[port][1]; // digit pin
  apin = mePort[port][0]; // analog pin

  speed = speed > 255 ? 255 : speed;
  speed = speed < -255 ? -255 : speed;

  if(speed >= 0) {
    pinMode(dpin, OUTPUT);
    digitalWrite(dpin, HIGH);
    analogWrite(apin, speed);  
  } else {
    pinMode(dpin, OUTPUT);
    digitalWrite(dpin, LOW);
    analogWrite(apin, -speed);  
  }
}

void parseCmd(char * cmd){
  Serial.println(cmd);
  if(cmd[0]=='M'){
    int spd0,spd1;
    sscanf(cmd,"M:%d,%d\n",&spd0,&spd1);
    doDcRun(M1,spd0);
    doDcRun(M2,spd1);
  }else if(cmd[0]=='H'){
    int pos0,pos1;
    sscanf(cmd,"H:%d,%d\n",&pos0,&pos1);
    servox.write(pos0);
    servoy.write(pos1);
  }

}


void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  servox.attach(A10);
  servoy.attach(A9);
  servox.write(90);
  servoy.write(90);
}

char buf[64];
char bufIndex=0;
void loop() {
  if(Serial1.available()){
    char c = Serial1.read();
    Serial.write(c);
    buf[bufIndex++]=c;
    if(c=='\n'){
      parseCmd(buf);
      bufIndex = 0;
      memset(buf,0,64);
    }
  }

}
