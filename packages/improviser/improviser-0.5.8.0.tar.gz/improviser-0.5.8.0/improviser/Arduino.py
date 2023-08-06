from threading import Thread
import serial
from os import sys
from time import sleep

class Arduino:

	def __init__(self):
		self.buf = BufferedRead()
		arduino = ReadArduinoUSB(self.buf)
		arduino.start()

	def get_last(self):
		r = self.buf.get_last()
		if r is not None and r != '':
			return r

class BufferedRead:

	values = [512, 512, 512, 512]
	stop = False
	
	def add(self, line):
		v = line.split(" ")
		self.values = map(lambda x: int(x), v)

	def get_last(self):
		return self.values

class ReadArduinoUSB(Thread):

	def __init__(self, buf):
		self.usb = serial.Serial("/dev/ttyUSB0", 9600)
		self.buf = buf
		Thread.__init__(self)

	def run(self):
		while not self.buf.stop:
			try:
				self.buf.add(self.usb.readline())
			except:
				self.usb.close()
				sys.exit(1)

