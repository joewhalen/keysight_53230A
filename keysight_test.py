import pyvisa
import config
from time import sleep

rm = pyvisa.ResourceManager()
inst = rm.open_resource(config.USB_ID)

inst.write('*RST')
sleep(0.1)
inst.write(f'SENS:FREQ:GATE:TIME {config.GATE_TIME};')
inst.write('SENS:FREQ:MODE REC;')
sleep(0.1)
inst.write('TRIG:SOUR IMM; COUN MAX')
sleep(0.1)
inst.write('INIT')

while True:
	print(inst.query('R?'))
	sleep(3)