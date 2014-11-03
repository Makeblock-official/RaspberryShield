import serial
import threading
import picamera
import time
import Image

#vectors L,F,R,B,U,D
#cent: -x +x -y +y
centF=["L","R","D","U"]
centR=["F","B","D","U"]

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


def parseColor(R,G,B):
    if R>30000 and G>30000 and B>30000:
        return "WHITE"
    elif R>30000 and G>30000 and B<5000:
        return "YELLOW"
    elif R<5000 and G<20000 and B>30000:
        return "BLUE"
    elif G>20000 and B<30000:
        return "GREEN"
    elif R>75000:
        return "ORANGE"
    elif R<75000:
        return "RED"
    else:
        print "unknow image",R,G,B
    

def parseFile(img):
    im = Image.open(img+".bmp")
    print im.mode,im.size,im.format
    box = (94, 21, 266, 207)
    reg = im.crop(box)
    reg = reg.rotate(0)
    reg.save(img+".test"+".bmp")
    idx=0
    for cb in colorbox:
    	regcolor = reg.crop(cb)
    	regcolor.save("%s.%d.bmp" %(img,idx))
        tmp = list(regcolor.getdata())
        R=G=B=0
        for pix in tmp:
            R=R+pix[0]
            G=G+pix[1]
            B=B+pix[2]
        c = parseColor(R,G,B)
        print img,idx,R,G,B,c
        idx=idx+1

def parseAllImage():
    for im in imglist:
        parseFile(im)

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

def rollUpLine(d):
	if d=="":

def moveX(m):
	if m=="in":
		cmd="A,0\nC,0\n"
		ser.write(cmd)
	elif m=="out":
		cmd="A,1\nC,1\n"
		ser.write(cmd)

def moveY(m):
	if m=="in":
		cmd="B,0\nD,0\n"
		ser.write(cmd)
	elif m=="out":
		cmd="B,1\nD,1\n"
		ser.write(cmd)

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

def centF():
	if cen=="F":
		print "error centF"
	if axis=="Y":
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
	setPos("F","X")


def centR(): # only front and right may play as center, make math easy
	if cen=="R":
		print "error centR"
	if axis=="Y":
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

	centR()
	delay(1)
	rollX(1)
	delay(1)
	getFig("B")
	centF()



cen=""
axis=""
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



