import pyvisa
import zmq
import config
from time import sleep

class Counter(object):

	def __init__(self):
		# define the counter parameters and the socket
		context = zmq.Context()
		rm = pyvisa.ResourceManager()

		self.socket = context.socket(zmq.PUB)
		self.socket.bind('tcp://*:'+config.PORT)
		self.inst = rm.open_resource(config.USB_ID)

		self.inst.write('*RST')
		self.inst.write(f'SENS:FREQ:GATE:TIME {config.GATE_TIME}; SENS:FREQ:MODE REC;')
		self.inst.write('TRIG:SOUR IMM; COUN MAX;')
		self.inst.write('SAMP:COUN MAX')


	def start_stream(self):
		self.inst.write('INIT')
		sleep(config.GATE_TIME)

		while True:
			r = self.inst.query('R?')
			if r != '#10\n':
				while r[0] != '+':
					r = r[1:]
				self.socket.send_string(r)

			sleep(config.TIME_BETWEEN_READS)


myCounter = Counter()
myCounter.start_stream()