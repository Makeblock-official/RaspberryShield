import struct
import serial
import threading
import time

rxbuff=bytearray()

slot1 = 1
slot2 = 2

axisX = 0
axisY = 1
axisZ = 2

port1 = 0x10
port2 = 0x20
port3 = 0x30
port4 = 0x40
port5 = 0x50
port6 = 0x60
port7 = 0x70
port8 = 0x80
m1 = 0x90
m2 = 0xA0
I2C =  0xB0
DIGIPORT = 0xC0
ALOGPORT = 0xD0

portEnum = {"Port1":port1,"Port2":port2,"Port3":port3,"Port4":port4,"Port5":port5,"Port6":port6,"Port7":port7,"Port8":port8,"M1":m1,"M2":m2,"I2C":I2C,0:0}
slotEnum = {"Slot1":slot1,"Slot2":slot2,0:0}
axisEnum = {"X-Axis":axisX,"Y-Axis":axisY,"Z-Axis":axisZ}
dpinEnum = {"D2":0,"D3":1,"D4":2,"D5":3,"D6":4,"D7":5,"D8":6,"D9":7,"D10":8,"D11":9,"D12":10,"D13":11}
apinEnum = {"A0":0,"A1":1,"A2":2,"A3":3,"A4":4,"A5":5}
pinmodeEnum = {"Input":1,"Output":0}
levelEnum = {"Low":0,"High":1,"Off":0,"On":1}

VERSION = 0
ULTRASONIC_SENSOR = 1
TEMPERATURE_SENSOR = 2
LIGHT_SENSOR = 3
POTENTIONMETER = 4
JOYSTICK = 5
GYRO = 6
RGBLED = 8
SEVSEG = 9
MOTOR = 10
SERVO = 11
ENCODER = 12
INFRARED = 16
LINEFOLLOWER = 17
    
DIGITAL_INPUT = 30
ANALOG_INPUT = 31
DIGITAL_OUTPUT = 32
ANALOG_OUTPUT = 33
PWM_OUTPUT = 34

moduleList = [] #{port:port2,slot:slot1,module:module}

class serialRead(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        while True:
            l = ser.readline()
            parsePackage(map(ord,l))

def b2f(s,pos_start):
    d =bytearray(s[pos_start:pos_start+4])
    f = struct.unpack("1f",str(d))[0]
    return f

def constructModule(module,portstr,slotstr,pin,value):
    port = portEnum[portstr]
    slot = slotEnum[slotstr]
    return {"port":port,"slot":slot,"module":module,"pin":pin,"value":[value]}


def appendModule(module,portstr,slotstr,pin):
    port = portEnum[portstr]
    slot = slotEnum[slotstr]
    for i in range(0,len(moduleList)):
        mod = moduleList[i];
        if mod["port"] == port and mod["slot"] == slot:
            # module at this port & slot changed
            if module != mod["module"]:
                mod["module"] = module
                mod["value"] = [] # reset the value to 0
            return i
    
    moduleList.append(constructModule(module,portstr,slotstr,pin,0));
    return len(moduleList)-1

def sendModuleList():
    #if(!device) return;
    modlen = len(moduleList)
    # ff 55 1 numdev dev1 port|slot 
    buff = bytearray()
    buff.append(0xff)
    buff.append(0x55)
    buff.append(0x01)
    buff.append(modlen*2)
    for i in range(0,len(moduleList)):
        mod = moduleList[i]
        buff.append(mod["module"])
        if mod["module"]>=DIGITAL_INPUT:
            buff.append(mod["pin"])
        else:
            buff.append(mod["port"]+mod["slot"])
    #print buff
    #device.send(buff.buffer);
    #print "Tx: %s" %list(buff)
    ser.write(buff)

def parsePackage(s):
    #print "Rx: %s" %s
    if(s[0]==0xff and s[1]==0x55):
        # ff 55 1 dev0[4] .... \r \n
        if(s[2]==0x01):
            dataLen = (len(s)-3-2)/4;
            moduleIndex = 0
            if(dataLen==0):
                return;
            for i in range(0,dataLen):
                if(moduleIndex>=len(moduleList)):
                    continue;
                # some special module may take multiple reply
                if(moduleList[moduleIndex]["module"] == JOYSTICK):
                    value = b2f(s,3+i*4)
                    i+=1
                    value2 = b2f(s,3+i*4)
                    moduleList[moduleIndex]["value"] = [value,value2]
                elif(moduleList[moduleIndex]["module"] == GYRO):
                    value = b2f(s,3+i*4);
                    i+=1
                    value2 = b2f(s,3+i*4);
                    i+=1
                    value3 = b2f(s,3+i*4);
                    moduleList[moduleIndex]["value"] = [value,value2,value3];
                else:
                    value = b2f(s,3+i*4);
                    moduleList[moduleIndex]["value"] = [value];
                moduleIndex+=1;
                
def deviceRun(mod):
    # ff 55 2 dev port|slot value[4]
    cc = bytearray()
    cc.append(0xff)
    cc.append(0x55)
    cc.append(0x02)
    cc.append(0x06) #the len of one device description
    cc.append(mod["module"])
    if mod["module"]>=DIGITAL_INPUT:
        cc.append(mod["pin"])
    else:
        cc.append(mod["port"]+mod["slot"])
        
    if(len(mod["value"])==1):
        f = struct.pack("@f",mod["value"][0])
        cc+=bytearray(f)
    elif len(mod["value"])==4:
        cc.append(mod["value"])
    print "run %s" %(list(cc))
    ser.write(cc)


ser = serial.Serial('/dev/ttyAMA0', 115200)
th = serialRead()
th.setDaemon(True)
th.start()

def doMotorRun(port,speed):
    mod=constructModule(MOTOR,port,"Slot1",0,speed)
    deviceRun(mod)
    
def doServoRun(port,slot,speed):
    mod=constructModule(SERVO,port,slot,0,speed)
    deviceRun(mod)


def doVersion():
    index = appendModule(VERSION,0,0,0)
    sendModuleList();
    return moduleList[index]["value"];

def doUltrasonic(port):
    index = appendModule(ULTRASONIC_SENSOR,port,"Slot1",0)
    sendModuleList()
    return moduleList[index]["value"][0]

def doLinefollow(port):
    index = appendModule(LINEFOLLOWER,port,"Slot1",0)
    sendModuleList()
    return moduleList[index]["value"][0]

def doLimitSwitch(port):

    return 0

def doTemperature(port,slot):
    index = appendModule(TEMPERATURE_SENSOR,port,slot,0)
    sendModuleList()
    return moduleList[index]["value"][0]

def doLightSensor(port,slot):
    index = appendModule(LIGHT_SENSOR,port,"Slot1",0)
    sendModuleList()
    return moduleList[index]["value"][0]

def doRunLightSensor(port,level):
    value = levelEnum[level]
    mod=constructModule(LIGHT_SENSOR,port,"Slot1",0,value)
    deviceRun(mod)

def doJoystick(port,axis):
    index = appendModule(JOYSTICK,port,"Slot1",0)
    sendModuleList()
    axis = axisEnum[axis]
    if axis == axisX:
        return moduleList[index]["value"][0]
    elif axis == axisY:
        return moduleList[index]["value"][1]

def doGyro(axis):
    index = appendModule(GYRO,"I2C","Slot1",0)
    sendModuleList()
    axis = axisEnum[axis]
    if axis == axisX:
        return moduleList[index]["value"][0]
    elif axis == axisY:
        return moduleList[index]["value"][1]
    elif axis == axisZ:
        return moduleList[index]["value"][2]

def doPotentialMeter(port):
    index = appendModule(POTENTIONMETER,port,"Slot2",0)
    sendModuleList()
    return moduleList[index]["value"][0]

def doInfrared (port):
    index = appendModule(INFRARED,port,"Slot1",0)
    sendModuleList()
    return moduleList[index]["value"][0]

def doRunSeg (port,num):
    mod=constructModule(SEVSEG,port,"Slot1",0,num)
    deviceRun(mod)
  
def doRunRgb (port,pixal,r,g,b):
    mod=constructModule(RGBLED,port,"Slot1",0,0)
    mod.value = [pixal,r,g,b]
    deviceRun(mod)
    
def doDWrite (pinstr,level):
    pin = dpinEnum[pinstr]
    value = levelEnum[level]
    mod = constructModule(DIGITAL_OUTPUT,"DIGIPORT","Slot1",0,0)
    mod["pin"] = pin+2 # +2 be compatable to arduino code
    mod["value"] = [value]
    deviceRun(mod)
    
def doAWrite (pinstr,value):
    pin = dpinEnum[pinstr]
    mod = constructModule(ANALOG_OUTPUT,"DIGIPORT","Slot1",0,value)
    mod["pin"] = pin+2 # +2 be compatable to arduino code
    mod["value"] = [value]
    deviceRun(mod)

def doDRead(pin):
    index = appendModule(DIGITAL_INPUT,"DIGIPORT","Slot1",pin)
    sendModuleList()
    pinvalue = moduleList[index].value[0];
    return pinvalue

def doARead(pin):
    index = appendModule(ANALOG_INPUT,"ALOGPORT","Slot1",pin);
    sendModuleList();
    pinvalue = moduleList[index].value[0];
    return pinvalue;

def resetAll():
    buff = bytearray()
    buff.append(0xff)
    buff.append(0x55)
    buff.append(0x04)
    buff.append(0x0)
    ser.write(buff)

doVersion()

    


