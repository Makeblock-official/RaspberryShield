import sys
import os
from xml.dom import minidom
import math
import serial
import threading
import time

busy=0
biasX=200
biasY=200
scaler=0.01
#const
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
        global busy
        while True:
            l = ser.readline()
            print l
            if "finally" in l:
                busy=0

def initBoard():
    cmd="I:0,0\n"
    ser.write(cmd)

def pen(pos):
    if pos>0:
        cmd="P:1\n"
        ser.write(cmd)
        time.sleep(0.2)
    else:
        cmd="P:0\n"
        ser.write(cmd)

def moveto(x,y):
    global posX,posY,stepA,stepB,busy
    x*=scaler
    y*=scaler
    x+=biasX
    y+=biasY
    print "move [%f,%f]" %(x,y)
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
    busy=1
    while busy>0:
        time.sleep(0.1) 
    

def parseRect(node):
    x = float(node.getAttribute("x"))
    y = float(node.getAttribute("y"))
    w = float(node.getAttribute("width"))
    h = float(node.getAttribute("height"))
    print ">> Rect",x,y,w,h
    pen(0)
    moveto(x,y)
    pen(1)
    moveto(x+w,y)
    moveto(x+w,y+h)
    moveto(x,y+h)
    moveto(x,y)
    pen(0)
    
    
def parseLine(node):
    x1 = float(node.getAttribute("x1"))
    x2 = float(node.getAttribute("x2"))
    y1 = float(node.getAttribute("y1"))
    y2 = float(node.getAttribute("y2"))
    print ">> Line",x1,y1,x2,y2
    pen(0)
    moveto(x1,y1)
    pen(1)
    moveto(x2,y2)
    pen(0)
    
    
def parsePolygon(node):
    pstr = node.getAttribute("points")
    points = pstr.split(" ")
    print ">> polygon:"
    isinit=0
    pen(0)
    initx=0
    inity=0
    for p in points:
        if len(p)==0: continue
        xstr,ystr = p.split(',')
        print ">>\t",xstr,ystr
        x=float(xstr)
        y=float(ystr)
        if isinit==0:
            moveto(x,y)
            initx=x
            inity=y
            pen(1)
            isinit=1
        else:
            moveto(x,y)
    moveto(initx,inity)
    pen(0)

def parsePolyline(node):
    pstr = node.getAttribute("points")
    points = pstr.split(" ")
    print ">> polyline:"
    isinit=0
    pen(0)
    for p in points:
        if len(p)==0: continue
        xstr,ystr = p.split(',')
        print ">>\t",xstr,ystr
        x=float(xstr)
        y=float(ystr)
        if isinit==0:
            moveto(x,y)
            pen(1)
            isinit=1
        else:
            moveto(x,y)
    pen(0)
    
def parsePath(node):
    d = node.getAttribute("d")
    ds=d.replace("c", " c ").replace("l", " l ").replace("-", " -").replace(",", " ").replace("M", "M ").replace("h", " h ").replace("m"," m ")
    ss=ds.replace("  ", " ").split(" ")
    print ss
    ptr=0
    state=""
    curvecnt=0 # todo: Bezier Curve
    pen(0)
    x=0
    y=0
    print ">> path:"
    while ptr<len(ss):
        #print "parse",ss[i]
        if ss[ptr].isalpha():
            print "into state",ss[ptr]
            state = ss[ptr]
            ptr+=1
            curvecnt=0
        else:
            if state=="h":
                dis=float(ss[ptr])
                print "h",dis
                ptr+=1
                moveto(x+dis,y)
            elif state=="v":
                dis=float(ss[ptr])
                print "v",dis
                ptr+=1
                moveto(x,y+dis)
            elif state=="M":
                x=float(ss[ptr])
                y=float(ss[ptr+1])
                ptr+=2
                print ">>\tM:x",x,"y",y
                moveto(x,y)
                pen(1)
            elif state=="m":
                dx=float(ss[ptr])
                dy=float(ss[ptr+1])
                ptr+=2
                print ">>\tm:x",x,"y",y
                pen(0)
                moveto(x+dx,y+dy)
                pen(1)
            elif state=="c":
                dx=float(ss[ptr])
                dy=float(ss[ptr+1])
                ptr+=2
                curvecnt+=1
                print ">>\tc:x",x,"y",y,"cnt",curvecnt
                if curvecnt==3:
                    moveto(x+dx,y+dy)
            elif state=="l":
                dx=float(ss[ptr])
                dy=float(ss[ptr+1])
                ptr+=2
                curvecnt+=1
                print ">>\tl:x",x,"y",y
                moveto(x+dx,y+dy)
            else:
                ptr+=1
                print "unknow state",state
    pen(0)
    

def parseNode(node):
    if node.nodeName=="path":
        parsePath(node)
    elif node.nodeName=="rect":
        parseRect(node)
    elif node.nodeName=="line":
        parseLine(node)
    elif node.nodeName=="polygon":
        parsePolygon(node)
    elif node.nodeName=="polyline":
        parsePolyline(node)
        
ser = serial.Serial('COM6', 115200)
th = serialRead()
th.start()
initBoard()

#dom = minidom.parse('littlerobot.svg')
dom = minidom.parse('tim.svg')
root = dom.documentElement
for node in root.childNodes:
    if node.nodeName=='g':
        for node1 in node.childNodes:
            parseNode(node1)
    else:
        parseNode(node)

print "####### Fin #######"
        
        








