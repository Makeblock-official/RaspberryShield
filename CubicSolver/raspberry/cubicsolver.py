import serial
import threading
import picamera
import time
import Image
import math
import sys,re  
import urllib,urllib2

#vectors L,F,R,B,U,D
#cent: -x +x -y +y
centF={"L":"left","R":"right","D":"lower","U":"upper"}
centR={"F":"left","B":"right","D":"lower","U":"upper"}
arms={"lower":["A","1"],"left":["B","2"],"upper":["C","3"],"right":["D","4"]}

x0=26
x1=78
x2=132
y0=25
y1=85
y2=149

c1=(x0,y0,x0+20,y0+20)
c2=(x1,y0,x1+20,y0+20)
c3=(x2,y0,x2+20,y0+20)

c4=(x0,y1,x0+20,y1+20)
c5=(x1,y1,x1+20,y1+20)
c6=(x2,y1,x2+20,y1+20)

c7=(x0,y2,x0+20,y2+20)
c8=(x1,y2,x1+20,y2+20)
c9=(x2,y2,x2+20,y2+20)

colorbox=[c1,c2,c3,c4,c5,c6,c7,c8,c9]
imglist=["L","F","R","B","U","D"]
colorMap={"L":"ORANGE","F":"GREEN","R":"RED","B":"BLUE","U":"WHITE","D":"YELLOW"}
colorMapRev={}
colorNumMap={"YELLOW":"1","RED":"2","BLUE":"3","WHITE":"4","GREEN":"5","ORANGE":"6"}
colorBlock={}
colorRef={}
colorArrange=["U","L","F","R","B","D"]



def parseColor(R,G,B):
    colorVectorDis={}
    for k,v in colorRef.iteritems():
        colorVectorDis[k]=math.sqrt(math.pow(R-v[0],2)+math.pow(G-v[1],2)+math.pow(B-v[2],2))
    dist=9999999
    mincolor=""
    
    for k,v in colorVectorDis.iteritems():
        if v<dist:
            dist=v
            mincolor=k
    return mincolor
   
def parseBlocks():
    colorArr={}
    for k, v in colorBlock.iteritems():
        colorStr=" "+k+":"
        idx=0
        for cb in colorbox:
            R=G=B=0
            regcolor = v.crop(cb)
            regcolor.save("%s.%d.bmp" %(k,idx))
            tmp = list(regcolor.getdata())
            for pix in tmp:
                R=R+pix[0]
                G=G+pix[1]
                B=B+pix[2]
            c = parseColor(R,G,B)
            colorStr+=colorNumMap[c]
            print k,idx,R,G,B,c
            idx=idx+1
        colorArr[k]=colorStr
    print colorArr
    return colorArr

def parseFile(img):
    im = Image.open(img+".bmp")
    print im.mode,im.size,im.format
    box = (89, 34, 262, 227)
    reg = im.crop(box)
    reg = reg.rotate(0)
    reg.save(img+".tmp"+".bmp")
    colorBlock[img]=reg
    refblock = reg.crop(colorbox[4])
    R=G=B=0
    tmp = list(refblock.getdata())
    for pix in tmp:
        R=R+pix[0]
        G=G+pix[1]
        B=B+pix[2]
    colorRef[colorMap[img]]=[R,G,B]

def parseAllImage():
	global str2send
	for im in imglist:
		parseFile(im)
	blockdict = parseBlocks()
	str2send = ""
	for c in colorArrange:
		mStr=blockdict[c]
		str2send+=mStr
	print str2send


def delay(i):
	time.sleep(i)

def setPos(c,ax):
	global cen,axis
	cen = c
	axis = ax

def rollX(d):
	if d==0:
		cmd="1,1\n3,1\n"
		ser.write(cmd)
	elif d==-1:# to left
		cmd="1,2\n3,0\n"
		ser.write(cmd)
	elif d==1:# to right
		cmd="1,0\n3,2\n"
		ser.write(cmd)

def rollY(d):
	if d==0:
		cmd="2,1\n4,1\n"
		ser.write(cmd)
	elif d==1:# to up
		cmd="2,2\n4,0\n"
		ser.write(cmd)
	elif d==-1:# to down
		cmd="2,0\n4,2\n"
		ser.write(cmd)

def rollArm(arm,d):
	print "roll",arm,d
	if d==2:
		rollArm(arm,1)
		rollArm(arm,1)
		return
	a = arms[arm][0] # the arm
	g = arms[arm][1] # the gripper
	cmd="%s,0\n" %(a)
	ser.write(cmd)
	delay(1)
	if d==-1:
		cmd = "%s,0\n" %(g)
		ser.write(cmd)
		delay(1)
	elif d==1:
		cmd = "%s,2\n" %(g)
		ser.write(cmd)
		delay(1)

	cmd="%s,1\n" %(a)
	ser.write(cmd)
	delay(1)
	cmd = "%s,1\n" %(g)
	ser.write(cmd)
	delay(1)
	cmd="%s,0\n" %(a)
	ser.write(cmd)
	delay(1)

def rollScript(face,d):
	if xstat=="out":
		moveX("in")
	if ystat=="out":
		moveY("in")
	if cen=="F":
		if centF.has_key(face):
			rollArm(centF[face],d)
		else:
			delay(1)
			centToR()
			rollScript(face,d)
	elif cen=="R":
		if centR.has_key(face):
			rollArm(centR[face],d)
		else:
			delay(1)
			centToF()
			rollScript(face,d)

def moveX(m):
	global xstat
	if m=="in":
		cmd="A,0\nC,0\n"
		ser.write(cmd)
		xstat="in"
	elif m=="out":
		cmd="A,1\nC,1\n"
		ser.write(cmd)
		xstat="out"


def moveY(m):
	global ystat
	if m=="in":
		cmd="B,0\nD,0\n"
		ser.write(cmd)
		ystat="in"
	elif m=="out":
		cmd="B,1\nD,1\n"
		ser.write(cmd)
		ystat="out"

def switchX():
	rollY(0)
	delay(1)
	moveX("in")
	delay(1)
	moveY("out")
	setPos(cen,"X")

def switchY():
	rollX(0)
	delay(1)
	moveY("in")
	delay(1)
	moveX("out")
	setPos(cen,"Y")

def centToF():
	if cen=="F":
		print "error centF"
	if xstat=="in" and ystat=="in":
		if axis=="Y":
			moveX("out")
		else:
			moveY("out")
		delay(1)
	elif axis=="Y":
		switchX()
		delay(1)
	rollX(-1)
	delay(1)
	moveY("in")
	delay(1)
	moveX("out")
	delay(1)
	rollX(0)
	delay(1)
	moveX("in")
	delay(1)
	moveY("out")
	delay(1)
	setPos("F","X")


def centToR(): # only front and right may play as center, make math easy
	if cen=="R":
		print "error centR"
	if xstat=="in" and ystat=="in":
		if axis=="Y":
			moveX("out")
		else:
			moveY("out")
		delay(1)
	elif axis=="Y":
		switchX()
		delay(1)
	rollX(1)
	delay(1)
	moveY("in")
	delay(1)
	moveX("out")
	delay(1)
	rollX(0)
	delay(1)
	moveX("in")
	delay(1)
	moveY("out")
	delay(1)
	setPos("R","X")



def getFig(fileName):
	delay(1)
	fileName=fileName+".bmp"
	camera.capture(fileName, format='bmp',resize=(320,240))

def cubicInitPos():
	moveX("out")
	delay(0.2)
	moveY("out")
	delay(0.2)
	rollX(0)
	delay(0.2)
	rollY(0)

def cubicIn():
	for i in range(5,0,-1):
		print "%d ...." %(i)
		delay(1)	
	moveX("in")
	setPos("F","X")

def takePics():
	rollX(0)
	delay(1)
	rollY(1)
	delay(1)
	moveY("in")
	delay(1)
	moveX("out")
	getFig("F")
	moveX("in")
	delay(1)
	moveY("out")
	delay(1)
	rollY(0)
	delay(1)
	
	rollX(-1)
	delay(1)
	getFig("L")
	
	rollX(1)
	delay(1)
	getFig("R")

	switchY()
	delay(1)
	rollY(-1)
	delay(1)
	getFig("D")

	rollY(1)
	delay(1)
	getFig("U")

	centToR()
	delay(1)
	rollX(1)
	delay(1)
	getFig("B")
	centToF()


def parseCodeLine(cc):
    mm = cc.split(" ")
    mcolor = mm[1]
    turnn = ""
    if(mm[3]=="1/2"):
        turnn = "2"
    elif mm[3]=="Clockwise":
        turnn = "1"
    elif mm[3]=="Counterclockwise":
        turnn = "-1"
    else:   
        print "unknow %s" %(mm[3])
    print "%s %s" %(mcolor, turnn)
    mface = colorMapRev[mcolor]
    return [mface,turnn]

def getMovement(moveStr):
	global moveList
	moveList=[]
	print "movestr=",moveStr
	url = "http://rubiksolve.com/cubesolve.php"  
	urllib2.urlopen('http://rubiksolve.com/').read() 
	params = urllib.urlencode([('cubevariablevalue', moveStr), ('solvesubmit', 'Solve Cube')])  
	# U:532241664 L:241664365 F:516555416 R:551623154 B:341233614 D:233412223
	# U:532241664 L:241664365 F:516555416 R:551623154 B:341233614 D:233412223
	req = urllib2.Request(url)  
	f = urllib2.urlopen(req,params)  
	retstr =  f.read()
	#print retstr

	b = retstr.find("<!--Start Table-->")
	c = retstr.find("<div id=\"sidebar\">")
	sool = retstr[b+1:c]
	print sool
	tmp = sool.split("Turn The")
	for m in tmp[1:]:
	    m = m[:m.find("</td>")]
	    #print m
	    moveList.append(parseCodeLine(m))
	print moveList

def solveRubik():
	for move in moveList:
		print "move",move
		rollScript(move[0],int(move[1]))


cen=""
axis=""
xstat="out"
ystat="out"
str2send=""
moveList=[]
for k,v in colorMap.iteritems():
	colorMapRev[v] = k
print "colorMapRev :",colorMapRev
camera = picamera.PiCamera()
ser = serial.Serial('/dev/ttyAMA0', 115200)
cmd="\r\n"
ser.write(cmd)

cubicInitPos()


#getFig("test.bmp")

while True:
	cmd = raw_input("Input command\n")
	parts = cmd.strip().split(" ")
	print parts
	if parts[0]=="fig":
		getFig("%s.bmp" %(parts[1]))
	elif parts[0]=="cubin":
		cubicIn()
	elif parts[0]=="init":
		cubicInitPos()
	elif parts[0]=="pic":
		takePics()
	elif parts[0]=="rollx":
		rollX(int(parts[1]))
	elif parts[0]=="rolly":
		rollY(int(parts[1]))
	elif parts[0]=="movex":
		moveX(parts[1])
	elif parts[0]=="movey":
		moveY(parts[1])
	elif parts[0]=="switch":
		if parts[1]=="x":
			switchX()
		if parts[1]=="y":
			switchY()
	elif parts[0]=="cent":
		if parts[1]=="f":
			centF()
		elif parts[1]=="r":
			centR()
	elif parts[0]=="color":
		parseAllImage()
	elif parts[0]=="getmove":
		getMovement(str2send)
	elif parts[0]=="scr":
		rollScript(parts[1],int(parts[2]))
	elif parts[0]=="solve":
		solveRubik()




