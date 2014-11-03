
from rpi_serial import *

while True:
	time.sleep(1)
	distance = doUltrasonic("Port3")
	print "distance",distance
