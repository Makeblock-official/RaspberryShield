'''
Created on 5.June.2014

@author: Riven
'''
import web
import serial
import threading
import socket
import fcntl
import struct
import time



port1=1
port2=2
port3=3
port4=4
port5=5
port6=6
port7=7
port8=8
m1=9
m2=10

slot1=0
slot2=1

DEV_NULL= "NULL"
DEV_ULTRASONIC= "Ultrasonic Sensor"
DEV_PIR= "PIR Motion Sensor"
DEV_BUTTON= "Button"
DEV_LIMIT= "Limit Switch"
DEV_POTENTIO= "Potentiometer"
DEV_LINEFINDER= "Line Finder"
DEV_SOUNDSENSOR= "Sound Sensor"
DEV_TEMPERATURE= "Temperature Sensor"
DEV_DCMOTOR= "DC Motor"
DEV_SERVO= "Servo Motor"
DEV_JOYSTICK= "Joystick"
DEV_LED= "Led"
DEV_IR= "Ir"
DEV_DPORT_READ= "R_DPORT"
DEV_APORT_READ= "R_APORT"
DEV_DPORT_WRITE= "W_DPORT"
DEV_APORT_WRITE="W_APORT"

class serialRead(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        while True:
            l = ser.readline()
            #print l
            parseEcho(l)

def isNumber(txt):
    try:
        int(txt,0)
        return True
    except:
        return False

def runmotor(left,right):
    cmd = "M:%d,%d\n" %(left,right)
    ser.write(cmd)
    print cmd
    
def runservo(axisx,axisy):
    cmd = "H:%d,%d\n" %(axisx,axisy)
    ser.write(cmd)
    print cmd


webtxt="""
<!DOCTYPE html>
<html>
<head>
<style type="text/css">
#joystick{
    position: absolute;
    top: 271px;
    left: 10px;
}
#head{
    position: absolute;
    top: 271px;
    left: 695px;
}
#distance{
    position: absolute;
    top: 10px;
    left: 10px;
    font-size:25px;
    color:#ff3300
}
</style>
<script type="text/javascript">
    //window.setInterval(getdistance,500)
    function getdistance()
    {
        dis = httpGet("/poll")
        console.log("distance",dis)
        document.getElementById("distance").innerHTML = dis

    }

    function httpGet(theUrl)
    {
        var xmlHttp = null;

        xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", theUrl, false );
        xmlHttp.send( null );
        return xmlHttp.responseText;
    } 
</script>
</head>
<body>
<div id="joystick">
    <img src="static/ctrl.png" usemap="#pad1" width="320" height="310" border="0">
    <map name="pad1">
    <area shape="rect" coords="124,41,195,113" onclick=httpGet("?move=forward") target="Message" alt="Move Forward" title="Move Forward">
    <area shape="rect" coords="38,118,117,191" onclick=httpGet("?move=left") target="Message" alt="Move Left" title="Move Left">
    <area shape="rect" coords="209,121,274,191" onclick=httpGet("?move=right") target="Message" alt="Move Right" title="Move Right">
    <area shape="rect" coords="126,196,195,268" onclick=httpGet("?move=backward") target="Message" alt="Move Backward" title="Move Backward">
    <area shape="rect" coords="128,126,196,188" onclick=httpGet("?move=stop") target="Message" alt="Stop" title="Stop">
    </map>
</div>
<div id="head">
    <img src="static/ctrl.png" usemap="#pad2" width="320" height="310" border="0">
    <map name="pad2">
    <area shape="rect" coords="124,41,195,113" onclick=httpGet("?head=up") target="Message" alt="Head Up" title="Head Up">
    <area shape="rect" coords="38,118,117,191" onclick=httpGet("?head=left") target="Message" alt="Head Left" title="Head Left">
    <area shape="rect" coords="209,121,274,191" onclick=httpGet("?head=right") target="Message" alt="Head Right" title="Head Right">
    <area shape="rect" coords="126,196,195,268" onclick=httpGet("?head=down") target="Message" alt="Head Down" title="Head Down">
    <area shape="rect" coords="128,126,196,188" onclick=httpGet("?head=origin") target="Message" alt="Back to Origin" title="Back to Origin">
    </map>
</div>


<div>
    <iframe src="http://HOSTIP:9000/stream_simple.html" width="100%" height="750" frameborder="no" border="0" marginwidth="0" marginheight="0" scrolling="no" allowtransparency="yes"></iframe>
</div>
<div id="distance">
@DIS
</div>

</body>
</html>
"""

urls = (
    '/', 'index',
    "/poll", "poll",
)

class index:
    def GET(self):
	global distance,posx,posy,spdl,spdr
        user_data = web.input()
        if user_data.has_key("move") : 
            if user_data.move == "forward":
                spdl = 80
                spdr = 80
            elif user_data.move == "backward":
                spdl = -80
                spdr = -80
            elif user_data.move == "left":
                spdl -= 20
                spdr += 20
            elif user_data.move == "right":
                spdl += 20
                spdr -= 20
            elif user_data.move == "stop":
                spdl = 0
                spdr = 0
            runmotor(spdl,spdr)
        if user_data.has_key("head"):
            print "head",user_data.head
            if user_data.head=="up":
                posx+=10
            elif user_data.head=="left":
                posy+=10
            elif user_data.head=="right":
                posy-=10
            elif user_data.head=="down":
                posx-=10
            elif user_data.head == "origin":
                posx = 90
                posy = 90
            if posx>=180:posx=180
            if posx<=0:posx=0
            if posy>=180:posy=180
            if posy<=0:posy=0
            runservo(posx,posy)

        print distance
    	strr = webtxt.replace("@DIS","%d cm" %(distance))
	return strr
    
class poll:
    def GET(self):
        global distance
        return "%d cm" %distance


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,
		struct.pack('256s',ifname[:15])
	)[20:24])
    
localIp = get_ip_address('wlan0')
print "localip =",localIp
webtxt = webtxt.replace("HOSTIP", localIp)
ser = serial.Serial('/dev/ttyAMA0', 115200)
#th = serialRead()
#th.setDaemon(True)
#th.start()
spdl = 0
spdr = 0
posx = 90
posy = 90
distance = 0
runservo(posx,posy)
runmotor(spdl,spdr)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()



