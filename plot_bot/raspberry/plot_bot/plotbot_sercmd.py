import math
import serial
import threading

mmtostep = 500/28.4707
Px=0
Py=0
Qx=880
Qy=0
posX=440
posY=354
stepA=0
stepB=0

class serialRead(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            l = ser.readline()
            print l

def moveTo(x,y):
    global posX,posY,stepA,stepB
    a0=math.sqrt(math.pow((posX-Px),2)+math.pow((posY-Py),2))
    b0=math.sqrt(math.pow((posX-Qx),2)+math.pow((posY-Qy),2))
    a1=math.sqrt(math.pow((x-Px),2)+math.pow((y-Py),2))
    b1=math.sqrt(math.pow((x-Qx),2)+math.pow((y-Qy),2))
    da=a1-a0
    db=b1-b0
    deltaStepA=da*mmtostep
    deltaStepB=db*mmtostep
    stepA+=deltaStepA
    stepB+=deltaStepB
    print "step",stepA,stepB
    posX=x
    posY=y
    cmd="G:%d,%d\n" %(math.trunc(stepA),math.trunc(stepB))
    ser.write(cmd)
    
ser = serial.Serial('COM6', 115200)
th = serialRead()
th.start()

while True:
    cmd = raw_input("Input command\n")
    parts = cmd.strip().split(" ")
    print parts
    if parts[0]=="move":
        tarX=float(parts[1])
        tarY=float(parts[2])
        moveTo(tarX,tarY)