import pyvisa
import zmq
import config
from time import sleep
from numpy.random import default_rng


class Counter(object):

	def __init__(self, virtual=False):
		# define the counter parameters and the socket
		self.virtual = virtual

		context = zmq.Context()		
		self.socket = context.socket(zmq.PUB)
		self.socket.bind('tcp://*:'+config.PORT)
		
		if not self.virtual:
			rm = pyvisa.ResourceManager()
			self.inst = rm.open_resource(config.USB_ID)
			self.inst.write('*RST')
			self.inst.write(f'SENS:FREQ:MODE RCON;')
			self.inst.write(f'SENS:FREQ:GATE:TIME {config.GATE_TIME};')
			#self.inst.write('TRIG:SOUR IMM; COUN MAX;')
			self.inst.write('SAMP:COUN MAX')		


	def start_stream(self):

		if self.virtual:
			rng = default_rng()
			f0 = 79.860e6
			sigma = 100
			while True:
				num = int(config.TIME_BETWEEN_READS/config.GATE_TIME + rng.integers(-2,2))
				freqs = f0 + sigma*rng.standard_normal(num)
				r = ','.join(['%+.15e'%i for i in freqs])+'\n'
				print(r)
				self.socket.send_string(r)
				sleep(1)
		else:
			self.inst.write('INIT')
			sleep(config.GATE_TIME)

			while True:
				r = self.inst.query('R?')
				if r != '#10\n':
					while r[0] != '+':
						r = r[1:]
					self.socket.send_string(r)

				sleep(config.TIME_BETWEEN_READS)


if __name__ == '__main__':

	import sys

	virtual = False
	if len(sys.argv) > 1:
		if sys.argv[1] == '-v':
			virtual = True
	
	myCounter = Counter(virtual)
	myCounter.start_stream()