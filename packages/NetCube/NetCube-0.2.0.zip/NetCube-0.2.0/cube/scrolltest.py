from Tkinter import *



# adapted from http://effbot.org/zone/tkinter-autoscrollbar.htm
# original by Fredrik Lundh

class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself it it's not needed.
    # only works if you use the grid geometry manager.
    # copied from http://effbot.org/zone/tkinter-autoscrollbar.htm

    def set(self, lo, hi):
	if float(lo) <= 0.0 and float(hi) >= 1.0:
	    # grid_remove is currently missing from Tkinter!
	    self.tk.call('grid', 'remove', self)
	else:
	    self.grid()
	    Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
	raise TclError, 'cannot use pack with this widget'
    def place(self, **kw):
	raise TclError, 'cannot use place with this widget!'


class ScrolledFrame(Frame):
    def __init__(self, *args, **kwargs):
	Frame.__init__(self, *args, **kwargs)

	self.vscrollbar = AutoScrollbar(self)
	self.vscrollbar.grid(row=0, column=1, sticky=N+S)
	self.hscrollbar = AutoScrollbar(self, orient=HORIZONTAL)
	self.hscrollbar.grid(row=1, column=0, sticky=E+W)

	self.canvas = Canvas(self,
	    yscrollcommand=self.vscrollbar.set,
	    xscrollcommand=self.hscrollbar.set)
	self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
	self.vscrollbar.config(command=self.canvas.yview)
	self.hscrollbar.config(command=self.canvas.xview)

	self.grid_rowconfigure(0, weight=1)
	self.grid_columnconfigure(0, weight=1)

	self.innerframe = Frame(self.canvas)

	self.canvas.create_window(0, 0, anchor=NW, window=self.innerframe)

	self.updateinner()

    def updateinner(self):
	self.innerframe.update_idletasks()
	self.canvas.config(scrollregion=self.canvas.bbox(ALL))

# create scrolled canvas
root = Tk()
f = Frame(root, relief='raised', bd='3') 
Label(f, text="howdy").pack()
f.pack()

frame = ScrolledFrame(root, relief='raised', bd='3')
frame.pack(expand=1, fill=BOTH)
iframe = frame.innerframe

iframe.rowconfigure(1, weight=1)
iframe.columnconfigure(1, weight=1)

rows = 5
for i in range(1, rows):
    for j in range(1, 10):
	button = Button(iframe, padx=7, pady=7, text="[%d,%d]" % (i, j))
	button.grid(row=i, column=j, sticky=N+E+W+S)

frame.updateinner()

root.mainloop()

def test1():
    root = Tk()

    vscrollbar = AutoScrollbar(root)
    vscrollbar.grid(row=0, column=1, sticky=N+S)
    hscrollbar = AutoScrollbar(root, orient=HORIZONTAL)
    hscrollbar.grid(row=1, column=0, sticky=E+W)

    canvas = Canvas(root,
	    yscrollcommand=vscrollbar.set,
	    xscrollcommand=hscrollbar.set)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)

    vscrollbar.config(command=canvas.yview)
    hscrollbar.config(command=canvas.xview)

    # make canvas expandable
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # create canvas contents
    frame = Frame(canvas)
    frame.rowconfigure(1, weight=1)
    frame.columnconfigure(1, weight=1)

    rows = 5
    for i in range(1, rows):
	for j in range(1, 10):
	    button = Button(frame, padx=7, pady=7, text="[%d,%d]" % (i, j))
	    button.grid(row=i, column=j, sticky=N+E+W+S)
	    
    canvas.create_window(0, 0, anchor=NW, window=frame)

    frame.update_idletasks()

    canvas.config(scrollregion=canvas.bbox(ALL))

    root.mainloop()
