#include <Makeblock.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include "I2Cdev.h"

// arduino only handle A,B step mapping
int initA,initB;
int posA,posB;
int tarA,tarB;
int pen; // the pen lifter
MePort stpB(PORT_1);
MePort stpA(PORT_2);
MeServo servoPen(PORT_3,DEV2);

/************** motor movements ******************/
void liftPen(int pen)
{
  Serial.printf("pen %d\n",pen);
  if(pen){
    servoPen.write(110);
  }else{
    servoPen.write(90);
  }
}

void stepperMoveA(int dir)
{
//  Serial.printf("stepper A %d\n",dir);
  if(dir>0){
    stpA.Dwrite1(LOW);
  }else{
    stpA.Dwrite1(HIGH);
  }
  stpA.Dwrite2(HIGH);
  delayMicroseconds(1);
  stpA.Dwrite2(LOW);
}

void stepperMoveB(int dir)
{
//  Serial.printf("stepper B %d\n",dir);
  if(dir>0){
    stpB.Dwrite1(LOW);
  }else{
    stpB.Dwrite1(HIGH);
  }
  stpB.Dwrite2(HIGH);
  delayMicroseconds(1);
  stpB.Dwrite2(LOW);
}

/************** calculate movements ******************/
#define SPEED_STEP 1
#define STEPDELAY_MIN 200 // micro second
#define STEPDELAY_MAX 1000
void movePen()
{
  int mDelay=STEPDELAY_MAX;
  int speedDiff = -SPEED_STEP;
  int dA,dB,maxD;
  float stepA,stepB,cntA=0,cntB=0;
  int d;
  dA = tarA - posA;
  dB = tarB - posB;
  maxD = max(abs(dA),abs(dB));
  stepA = (float)abs(dA)/(float)maxD;
  stepB = (float)abs(dB)/(float)maxD;
  Serial.printf("move: max:%d da:%d db:%d\n",maxD,dA,dB);
  Serial1.printf("move: max:%d da:%d db:%d\n",maxD,dA,dB);
  Serial.print(stepA);Serial.print(' ');Serial.println(stepB);
  Serial1.print(stepA);Serial.print(' ');Serial.println(stepB);
  for(int i=0;i<=maxD;i++){
    //Serial.printf("step %d A:%d B;%d\n",i,posA,posB);
    // move A
    if(posA!=tarA){
      cntA+=stepA;
      if(cntA>=1){
        d = dA>0?1:-1;
        stepperMoveA(d);
        cntA-=1;
        posA+=d;
      }
    }
    // move B
    if(posB!=tarB){
      cntB+=stepB;
      if(cntB>=1){
        d = dB>0?1:-1;
        stepperMoveB(d);
        cntB-=1;
        posB+=d;
      }
    }
    mDelay=constrain(mDelay+speedDiff,STEPDELAY_MIN,STEPDELAY_MAX);
    delayMicroseconds(mDelay);
    if((maxD-i)<((STEPDELAY_MAX-STEPDELAY_MIN)/SPEED_STEP)){
      speedDiff=SPEED_STEP;
    }
  }
  Serial.printf("finally %d A:%d B;%d\n",maxD,posA,posB);
  Serial1.printf("finally %d A:%d B;%d\n",maxD,posA,posB);
  posA = tarA;
  posB = tarB;
}

/************** calculate movements ******************/
void parseCmd(char * cmd)
{
  if(cmd[0]=='I'){
    sscanf(cmd,"I:%d,%d\n",&initA,&initB);
    posA = initA;
    posB = initB;
    tarA = initA;
    tarB = initB;
    Serial.printf("initA=%d,initB=%d\n",initA,initB);
    Serial1.printf("initA=%d,initB=%d\n",initA,initB);
  }else if(cmd[0]=='G'){
    sscanf(cmd,"G:%d,%d\n",&tarA,&tarB);
    if(tarA==posA && tarB==posB){
      Serial.printf("finally %d A:%d B;%d\n",0,posA,posB);
      Serial1.printf("finally %d A:%d B;%d\n",0,posA,posB);
    }
  }else if(cmd[0]=='P'){
    sscanf(cmd,"P:%d\n",&pen);
    liftPen(pen);
  }else if(cmd[0]=='A'){
    Serial.printf("pos:%d,%d\n",posA,posB);
    Serial1.printf("pos:%d,%d\n",posA,posB);
  }
}

/************** arduino ******************/
void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  servoPen.begin();
}

char buf[64];
char bufindex;
char buf2[64];
char bufindex2;

void loop() {
  if(Serial.available()){
    char c = Serial.read();
    buf[bufindex++]=c;
    if(c=='\n'){
      parseCmd(buf);
      memset(buf,0,64);
      bufindex = 0;
    }
  }
  if(Serial1.available()){
    char c = Serial1.read();
    buf2[bufindex2++]=c;
    if(c=='\n'){
      parseCmd(buf2);
      memset(buf2,0,64);
      bufindex2 = 0;
    }
  }
  
  if(posA!=tarA || posB!=tarB){
    Serial.printf("diff %d %d %d %d\n",posA,tarA,posB,tarB);
    Serial1.printf("diff %d %d %d %d\n",posA,tarA,posB,tarB);
    movePen();
  }
}
