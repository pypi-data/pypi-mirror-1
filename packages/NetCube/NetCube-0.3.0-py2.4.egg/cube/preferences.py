#!/usr/bin/env pythonw

# Copyright 2005 Jeffrey J. Kyllo

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from Tkinter import *

def colorwell(master=None, var=None, cnf={}, **kw):
    """
    creates a frame with controls.
    creates a variable that is used to set the color well background.
    sets up button to change variable based on colorpicker
    """

    def tkcolor_to_cubecolor(tkcolor):
	"""Converts a color from a Tkinter colorpicker into a color usable by NetCube."""
        import re
        short_fmt = re.compile('^#([0-f])([0-f])([0-f])$')
        long_fmt = re.compile('^#([0-f]{2})([0-f]{2})([0-f]{2})$')

        m = short_fmt.match(tkcolor)
        if m is None:
            m = long_fmt.match(tkcolor)

        if m is not None:    
            vals = [str(int(x,16) / 255.0) for x in m.groups()]
	    ret = ','.join(vals) + ',0.5'
	    #print "colorwell returning: %s" % ret
            return ret

        return None
        
    def cubecolor_to_tkcolor(cubecolor):
	"""Converts a color from the NetCube into a color usable by a Tkinter colorpicker."""
        import re
        fmt = re.compile('^(\d+(\.\d*)?|\.\d+),(\d+(\.\d*)?|\.\d+),(\d+(\.\d*)?|\.\d+),(\d+(\.\d*)?|\.\d+)$')
        m = fmt.match(cubecolor)
        if m is not None:
            vals = [hex(int(float(x) * 255)) for x in m.group(1,3,5)]
            simp = re.compile('0x([0-f]+)')
            vals = [simp.match(x).expand('\\1').zfill(2) for x in vals]
            return '#' + ''.join(vals)
    
    f = Frame(master, cnf, *kw)
    cnvs = Canvas(f, width=20, height=15)

    
    if var is None:
        var = Variable()
        var.set('1.0,1.0,1.0,0.5')
    else:
        r = var.get()
        
    def callback(*args):
	"""Called when the NetCube's color list is updated.  This converts the
	color and sets it on the colorwell's preview area."""
        tmp = var.get()
        if tmp is not None:
            c = cubecolor_to_tkcolor(tmp)
            cnvs['background'] = c

    var.trace_variable('w', callback)
    callback()
    cnvs.pack({'side': 'left'})

    def pickcolor():
	"""Called when the colorwell's Choose button is clicked.  This launches
	a Tkinter color picker dialog for user selection of a color and then
	stores that color in the color preview area."""
        import tkColorChooser
        color = tkColorChooser.askcolor(cubecolor_to_tkcolor(var.get()))[1]
        if color is not None:
            c = tkcolor_to_cubecolor(color)
            var.set(c)

    btn = Button(f, text='choose', command=pickcolor)
    btn.pack({'side': 'left'})
    return f


class AutoScrollbar(Scrollbar):
    """
    a scrollbar that hides itself if it's not needed.
    only works if you use the grid geometry manager.
    copied from http://effbot.org/zone/tkinter-autoscrollbar.htm
    original by Fredrik Lundh
    """

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
    """
    adapted from http://effbot.org/zone/tkinter-autoscrollbar.htm
    adapted from code by Fredrik Lundh
    """
    def __init__(self, *args, **kwargs):
	Frame.__init__(self, *args, **kwargs)

	width=None
	if kwargs.has_key('width'):
	    width=kwargs['width']

	height=None
	if kwargs.has_key('height'):
	    height=kwargs['height']

	self.vscrollbar = AutoScrollbar(self)
	self.vscrollbar.grid(row=0, column=1, sticky=N+S)
	self.hscrollbar = AutoScrollbar(self, orient=HORIZONTAL)
	self.hscrollbar.grid(row=1, column=0, sticky=E+W)

	self.canvas = Canvas(self,
	    yscrollcommand=self.vscrollbar.set,
	    xscrollcommand=self.hscrollbar.set, width=width, height=height)
	self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
	self.vscrollbar.config(command=self.canvas.yview)
	self.hscrollbar.config(command=self.canvas.xview)

	self.grid_rowconfigure(0, weight=1)
	self.grid_columnconfigure(0, weight=1)

	self.innerframe = Frame(self.canvas)
	self.innerframe.bind('<Configure>', lambda event: self.updateinner())

	self.canvas.create_window(0, 0, anchor=NW, window=self.innerframe)

	self.updateinner()

    def updateinner(self):
	self.innerframe.update_idletasks()
	self.canvas.config(scrollregion=self.canvas.bbox(ALL))



from tkFileDialog import *



def propsheet(config=None, master=None, **kwargs):
    """Creates a preference window (in a Frame).  If config is given then the controls
    are bound to the variables found in that config.  config is a dictionary of dictionaries.
    The outer dictionary has setion names as keys.  The inner dictionaries have option
    names as keys and Variables as values."""

    
    root = master

    #win = Frame(root, *kwargs)
    win = ScrolledFrame(root, **kwargs)

    iframe = win.innerframe
    #win.pack()
    
    win.config = config
    
    var_for = lambda s, o: _var_for(config, s, o)
    def _var_for(config, section, option):
	if config is not None: 
	    return config.var_for(section, option)
	else:
	    return Variable()

        if not config.has_key(section):
            config[section] = {}
            
        if not config[section].has_key(option) or config[section][option] is None:
            config[section][option] = Variable()

        var = config[section][option]
	#print "Retrieving var: %s.%s, with value=%s" % (section, option, var.get())
        return var
    
    win.networksettings = LabelFrame(iframe, relief='raised', borderwidth=1, text='Network', padx=15, pady=15)
    win.networksettings.pack(fill=X, expand=1)
    #win.networksettings.col1 = Frame(win.networksettings, padx=15, pady=15)
    #win.networksettings.col1.pack({'side': 'left'})

    frame = Frame(win.networksettings)
    frame.pack()
    Label(frame, text='Interface').pack({'side': 'left'})

    import pcapy
    interfaces = pcapy.findalldevs()
    interstr = ""
    for i in interfaces:
	if len(interstr) > 0:
	    interstr += " "
	interstr += i
    interfacevar = var_for('capture', 'interface')
    om = OptionMenu(frame, interfacevar, *interfaces)
    om.pack({'side': 'left'})


    #resVar = StringVar()
    #resVar.set('320x240')
    #om = OptionMenu(win.displaysettings.col1.screen.resolution, resVar, '640x480', '320x240', '160x120')
    #om.pack()


    win.networksettings.promisc = Checkbutton(win.networksettings, text='Promiscuous capture', variable=var_for('capture', 'promisc'))
    win.networksettings.promisc.pack()
    

    labelcol = Frame(win.networksettings)
    labelcol.pack({'side': 'left'})
    valuecol = Frame(win.networksettings)
    valuecol.pack({'side': 'left'})

    Label(labelcol, text='Read capture file:').pack()
    frame = Frame(valuecol)
    frame.pack()
    win.networksettings.read = Entry(frame, textvariable=var_for('capture', 'read'))
    win.networksettings.read.pack({'side': 'left'})
    def choosereadfile(entry):
	fname = askopenfilename(filetypes=[('PCap file', '*.cap *.pcap')], defaultextension='.cap')
	var_for('capture', 'read').set(fname)
    btn = Button(frame, text='Choose', command=lambda: choosereadfile(win.networksettings.read))
    btn.pack({'side': 'left'})



    Label(labelcol, text='Write capture file:').pack()
    frame = Frame(valuecol)
    frame.pack()
    win.networksettings.write = Entry(frame, textvariable=var_for('capture', 'write'))
    win.networksettings.write.pack({'side': 'left'})
    def choosesaveasfile(entry):
	fname = asksaveasfilename(filetypes=[('PCap file', '*.cap *.pcap')], defaultextension='.cap')
	var_for('capture', 'write').set(fname)
    btn = Button(frame, text='Choose', command=lambda: choosesaveasfile(win.networksettings.write))
    btn.pack({'side': 'left'})


    Label(labelcol, text='Capture filter:').pack({'side': 'left'})
    win.networksettings.filter = Entry(valuecol, textvariable=var_for('capture', 'filter'), width=27)
    win.networksettings.filter.pack({'side': 'left'})




    
    #win.displaysettings = LabelFrame(iframe, relief='ridge', borderwidth=2, text='Display', width=200)
    #win.displaysettings.pack({'side': 'left'})
    #win.displaysettings.col1 = Frame(win.displaysettings, padx=15, pady=15)
    #win.displaysettings.col1.pack({'side':'left'})

    #win.displaysettings.col1.screen = LabelFrame(win.displaysettings.col1, relief='raised', borderwidth=1, text='Screen', padx=15, pady=15)
    win.screen = LabelFrame(iframe, relief='raised', borderwidth=1, text='Screen', padx=15, pady=15)
    win.screen.pack(fill=X, expand=1)
    
    win.screen.fullscreen = Checkbutton(win.screen, text='Fullscreen', variable=var_for('display', 'fullscreen'))
    win.screen.fullscreen.pack()
    control = win.screen.fullscreen
    
    win.screen.resolution = Frame(win.screen)
    caption = Label(win.screen.resolution, text='Resolution:')
    caption.pack({'side': 'left'})
    #resVar = StringVar()
    #resVar.set('320x240')
    #om = OptionMenu(win.displaysettings.col1.screen.resolution, resVar, '640x480', '320x240', '160x120')
    #om.pack()
    e1 = Entry(win.screen.resolution, width=5, textvariable=var_for('display', 'width'))
    e1.pack({'side': 'left'})
    win.screen.resolution.width = e1
    Label(win.screen.resolution, text="x").pack({'side': 'left'})
    e1 = Entry(win.screen.resolution, width=5, textvariable=var_for('display', 'height'))
    e1.pack({'side': 'left'})
    win.screen.resolution.height = e1

    win.screen.resolution.pack()
    sl = Scale(win.screen, orient='horizontal', label='Frame rate:', length=150, variable=var_for('display', 'fps'))
    sl['from'] = 0
    sl['to'] = 30
    sl.pack()

    #win.displaysettings.col1.datapoints = LabelFrame(win.displaysettings.col1, relief='raised', borderwidth=1, text='Data Points', padx=15, pady=15)
    win.datapoints = LabelFrame(iframe, relief='raised', borderwidth=1, text='Data Points', padx=15, pady=15)
    win.datapoints.pack(fill=X, expand=1)

    s1 = Scale(win.datapoints, orient='horizontal', label='Point size:', length=150, variable=var_for('display', 'pointsize'))
    s1['from'] = 1
    s1['to'] = 10
    s1.pack()

    f1 = Frame(win.datapoints)
    l1 = Label(f1, text="Point TTL:")
    l1.pack({'side': 'left'})
    e = Entry(f1, width=5, textvariable=var_for('graphics', 'ttl'))
    e.pack({'side': 'left'})
    f1.pack()

    f1 = Frame(win.datapoints)
    lv = Variable()
    lv.set('"howdy there"')
    lb = Listbox(f1, listvariable=lv, height=5, state='disabled')
    lb.pack({'side': 'left'})
    f2 = Frame(f1)
    f3 = Frame(f2)
    Label(f3, text="Port:", state='disabled').pack({'side': 'left'})
    Entry(f3, width=5, state='disabled').pack({'side': 'left'})
    f3.pack(anchor='w')
    f3 = Frame(f2)
    Label(f3, text="Color:", state='disabled').pack({'side': 'left'})
    cw = colorwell(f3)
    cw.pack({'side': 'left'})
    f3.pack(anchor='w')
    f2.pack({'side': 'left'})
    f1.pack()

    #win.displaysettings.col1.datacube = LabelFrame(win.displaysettings.col1, relief='raised', borderwidth=1, text='Data Cube', padx=15, pady=15)
    win.datacube = LabelFrame(iframe, relief='raised', borderwidth=1, text='Data Cube', padx=15, pady=15)
    win.datacube.pack(fill=X, expand=1)

    sl = Scale(win.datacube, orient='horizontal', label='Line width:', length=150, variable=var_for('display', 'linewidth'))
    sl['from'] = 1
    sl['to'] = 10
    sl.pack()

    sl = Scale(win.datacube, orient='horizontal', label='Spin rate (degrees/sec.)', length=150, variable=var_for('graphics', 'spin'))
    sl['from'] = 0
    sl['to'] = 360
    sl.pack()

    win.datacube.axislabels = Checkbutton(win.datacube, text='Show Axis Labels', variable=var_for('graphics', 'axislabels'))
    win.datacube.axislabels.pack()

    win.datacube.axiscolor = LabelFrame(win.datacube, relief='ridge', borderwidth=2, text='Axis color')
    
    f1 = Frame(win.datacube.axiscolor)
    lbl = Label(f1, text='X axis:')
    lbl.pack({'side': 'left'})
    cx = var_for('graphics', 'xcolor')
    #cx.set('1.0,0.0,0.0,0.0')
    well = colorwell(f1, cx)
    well.pack({'side' : 'left'})
    f1.pack()

    f1 = Frame(win.datacube.axiscolor)
    lbl = Label(f1, text='Y axis:')
    lbl.pack({'side': 'left'})
    cy = var_for('graphics', 'ycolor')
    #cy.set('0.0,1.0,0.0,0.0')
    well = colorwell(f1, cy)
    well.pack({'side' : 'left'})
    f1.pack()

    f1 = Frame(win.datacube.axiscolor)
    lbl = Label(f1, text='Z axis:')
    lbl.pack({'side': 'left'})
    cz = var_for('graphics', 'zcolor')
    #cz.set('0.0,0.0,1.0,0.0')
    well = colorwell(f1, cz)
    well.pack({'side' : 'left'})
    f1.pack()

    win.datacube.axiscolor.pack()


    def axisrange(master=None):
        f1 = Frame(master)
        f2 = Frame(f1)

        radiovar = Variable()
        #radiovar.set('range')



        
        f3 = Frame(f2)
        f1.range = f3
        r1 = Radiobutton(f3, text='min', variable=radiovar, value='range')
        r1.pack({'side': 'left'})
        f3.radio = r1
        e1 = Entry(f3, width=15)
        e1.pack({'side': 'left'})
        f3.minentry = e1
        l1 = Label(f3, text='max')
        l1.pack({'side': 'left'})
        f3.maxlabel = l1
        e1 = Entry(f3, width=15)
        e1.pack({'side': 'left'})
        f3.maxentry = e1
        f3.pack(anchor='w')

        f3 = Frame(f2)
        f1.cidr = f3
        r2 = Radiobutton(f3, text='IP Address', variable=radiovar, value="cidr")
        r2.pack({'side': 'left'})
        f3.radio = r2
        e2 = Entry(f3, width=15)
        e2.pack({'side': 'left'})
        f3.ip = e2
        l2 = Label(f3, text='/')
        l2.pack({'side': 'left'})
        e2 = Entry(f3, width=5)
        e2.pack({'side': 'left'})
        f3.mask = e2
        f3.pack(anchor='w')

        f3 = Frame(f2)
        f1.device = f3
        r2 = Radiobutton(f3, text='Use device range', variable=radiovar, value="device")
        r2.pack({'side': 'left'})

        f3.radio = r2
        f3.pack(anchor='w')
        
        f2.pack()
        #f1.range.radio.select()
        f1.var = radiovar
        #print "radiovar=%s" % radiovar
        return f1

    def update_devrange_var(dr_var, radio_var):
        rv = radio_var.get()
        if rv == 'device':
            dr_var.set(True)
        else:
            dr_var.set(False)
            

    #win.displaysettings.col2 = Frame(win.displaysettings, padx=15, pady=15)
    #win.displaysettings.col2.axisrange = LabelFrame(win.displaysettings.col2, relief='raised', borderwidth=1, text='Axis Ranges', padx=15, pady=15)
    win.axisrange = LabelFrame(iframe, relief='raised', borderwidth=1, text='Axis Ranges', padx=15, pady=15)
    
    f1 = LabelFrame(win.axisrange, text='X axis', padx=15, pady=15)
    win.axisrange.x = f1
    f1.frame = axisrange(f1)
    #f1.frame.var.trace('w', lambda *args: update_devrange_var(var_for('display', 'xusedevrange'), f1.frame.var))
    f1.frame.pack()
    f1.pack()
    
    f1.frame.range.minentry['textvariable'] = var_for('graphics', 'xmin')
    f1.frame.range.maxentry['textvariable'] = var_for('graphics', 'xmax')
    f1.frame.cidr.ip['textvariable'] = var_for('graphics', 'xcidrip')
    f1.frame.cidr.mask['textvariable'] = var_for('graphics', 'xcidrmask')

    v = var_for('graphics', 'xbounds')
    f1.frame.range.radio['variable'] = v
    f1.frame.cidr.radio['variable'] = v
    f1.frame.device.radio['variable'] = v
    if v is not None and v.get() not in ['range', 'cidr', 'device']:
        f1.frame.range.radio.select()
    
    ef1 = LabelFrame(win.axisrange, text='Y axis', padx=15, pady=15)
    win.axisrange.y = ef1
    f2 = Frame(ef1)
    #ymin = Variable()
    #ymin.set(0)
    #ymax = Variable()
    #ymax.set(65535)
    Label(f2, text="min").pack({'side': 'left'}, anchor='w')
    Entry(f2, width=5, textvariable=var_for('graphics', 'ymin')).pack({'side': 'left'}, anchor='w')
    Label(f2, text="max").pack({'side': 'left'}, anchor='w')
    Entry(f2, width=5, textvariable=var_for('graphics', 'ymax')).pack({'side': 'left'}, anchor='w')
    f2.pack()
    ef1.pack()

    af1 = LabelFrame(win.axisrange, text='Z axis', padx=15, pady=15)
    win.axisrange.z = af1
    af1.frame = axisrange(af1)
    #af1.frame.var.trace('w', lambda *args: update_devrange_var(var_for('display', 'zusedevrange'), af1.frame.var))
    af1.frame.pack()
    af1.pack()

    af1.frame.range.minentry['textvariable'] = var_for('graphics', 'zmin')
    af1.frame.range.maxentry['textvariable'] = var_for('graphics', 'zmax')
    af1.frame.cidr.ip['textvariable'] = var_for('graphics', 'zcidrip')
    af1.frame.cidr.mask['textvariable'] = var_for('graphics', 'zcidrmask')

    v = var_for('graphics', 'zbounds')
    af1.frame.range.radio['variable'] = v
    af1.frame.cidr.radio['variable'] = v
    af1.frame.device.radio['variable'] = v
    if v is not None and v.get() not in ['range', 'cidr', 'device']:
        af1.frame.range.radio.select()
    
    win.axisrange.pack(fill=X, expand=1)
    #win.displaysettings.col2.pack({'side':'left'}, anchor='n', ipady=15)

    win.updateinner()
    
    return win

if __name__ == '__main__':
    root = Tk()
    root.title('NetCube Preferences')
    root.withdraw()
    ps = propsheet(master=root, width=327, height=100)
    ps.pack(expand=1, fill=BOTH)
    root.deiconify()
    mainloop()
