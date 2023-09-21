import tkinter as tk

from matplotlib.backends.backend_tkagg import (
	FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import allantools as at

from numpy.random import default_rng
import numpy as np

import zmq

import config

rng = default_rng()

class MyApp(tk.Tk):

	def __init__(self, *args, **kwargs):

		tk.Tk.__init__(self, *args, **kwargs)
		
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.SUB)
		self.socket.connect('tcp://localhost:'+config.PORT)
		self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

		self.initialized = False
		self.allan_update_time = 10
		self.time_series_record_length = 250

		self.t = np.array([])
		self.f = np.array([])

		self.time_series_fig = FigureFrame(self)
		self.allan_dev_fig = FigureFrame(self)

		self.allan_dev_fig.ax.set_xscale('log')
		self.allan_dev_fig.ax.set_yscale('log')

		go_button = tk.Button(text='GO', command = self.read_data_stream)
		quit_button = tk.Button(text='Quit', command = self.destroy)
		
		#go_button.pack()
		self.time_series_fig.pack()
		self.allan_dev_fig.pack()
		quit_button.pack()

		self.read_data_stream()
		self.update_allan_dev()



	def read_data_stream(self):
		
		r = np.array([float(i) for i in self.socket.recv_string().split(',')])
		print(r)
		if self.initialized:
			self.t = np.concatenate((self.t, np.arange(len(r))*config.GATE_TIME + self.t[-1]))
		else:
			self.t = np.concatenate((self.t, np.arange(len(r))*config.GATE_TIME))
			self.initialized = True

		self.f = np.concatenate((self.f, r))

		if len(self.t > self.time_series_record_length):
			self.time_series_fig.redraw(x=self.t[-self.time_series_record_length:],
			 							y=self.f[-self.time_series_record_length:])
		else:
			self.time_series_fig.redraw(x=self.t,y=self.f)
		self.after(950 * config.TIME_BETWEEN_READS, self.read_data_stream)

	def update_allan_dev(self):

		taus, ad, ade, ns = at.oadev(self.f, rate=1/config.GATE_TIME, data_type='freq')
		self.allan_dev_fig.redraw(x=taus, y=ad)

		self.after(self.allan_update_time * 1000, self.update_allan_dev)



class FigureFrame(tk.Frame):

	def __init__(self, parent):
		
		tk.Frame.__init__(self, parent)
		
		self.x = np.linspace(0,10,100)
		self.y = rng.random(len(self.x))

		self.fig = Figure(figsize=(5,4), dpi=100)
		self.ax = self.fig.add_subplot()
		self.line, = self.ax.plot(self.x,self.y)
		self.ax.set_xlabel('t')
		self.ax.set_ylabel('Frequency (Hz)')


		self.canvas = FigureCanvasTkAgg(self.fig, master=self)
		self.canvas.draw()
		self.toolbar = NavigationToolbar2Tk(self.canvas, self, 
			pack_toolbar=False)

		self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, 
			expand=True)

	def redraw(self, x=[], y=[]):
		#print(x[0],y[0])
		self.line.set_data(x,y)
		self.ax.relim()
		self.ax.autoscale_view()

		self.canvas.draw()


if __name__ == '__main__':

	app = MyApp()
	app.mainloop()