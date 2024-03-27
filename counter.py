import pyvisa
import zmq
import config
from time import sleep
from numpy.random import default_rng
import argparse


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

class CounterParser(argparse.ArgumentParser):
	def __init__(self):
		argparse.ArgumentParser.__init__(self)
		self.add_argument('-v', '--virtual', help='Virtual counter mode.',
					action='store_true')



if __name__ == '__main__':

	parser = CounterParser()
	args = parser.parse_args()
	
	if args.virtual:
		print('Using Virtual Counter')
		myCounter = Counter(virtual=True)
	else:
		myCounter = Counter()
	myCounter.start_stream()