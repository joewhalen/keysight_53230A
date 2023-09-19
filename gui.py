import tkinter as tk

# will need allantools and matplotlib

class MyApp(tk.Tk):

	def __init__(self, *args, **kwargs):

		tk.Tk.__init__(self, *args, **kwargs)

		frame = tk.Frame()

app = MyApp()

app.mainloop()