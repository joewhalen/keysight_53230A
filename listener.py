import zmq
import config

context = zmq.Context()

socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:'+config.PORT)
socket.setsockopt_string(zmq.SUBSCRIBE, '')

while True:
	string = socket.recv_string()
	print(f'Received {string}')