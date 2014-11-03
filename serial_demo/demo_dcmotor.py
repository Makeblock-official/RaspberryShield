from rpi_serial import *

while True:
	cmd = raw_input("Input motor speed\n")
	try:
	    speed = int(cmd)
	    doMotorRun("M1",speed)
	except ValueError:
	    print "please input a number"


