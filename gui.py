import tkinter as tk

from matplotlib.backends.backend_tkagg import (
	FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import allantools as at

from numpy.random import default_rng
import numpy as np

import zmq

rng = default_rng()

class MyApp(tk.Tk):

	def __init__(self, *args, **kwargs):

		tk.Tk.__init__(self, *args, **kwargs)

		time_series_fig = FigureFrame(self)
		go_button = tk.Button(text='Update Plot', command = time_series_fig.redraw)
		quit_button = tk.Button(text='Quit', command = self.destroy)
		go_button.pack()
		time_series_fig.pack()
		quit_button.pack()


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
		self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)

		self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def redraw(self, data=[]):
		self.line.set_data(data)
		self.canvas.draw()


if __name__ == '__main__':

	app = MyApp()
	app.mainloop()