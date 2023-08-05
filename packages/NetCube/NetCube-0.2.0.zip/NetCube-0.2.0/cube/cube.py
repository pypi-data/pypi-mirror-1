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


from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import os
import pygame
from pygame.locals import *
import pygame.mouse
import random
import pcapy
import socket
import struct
import time
import string
from optparse import OptionParser
import re
from ConfigParser import SafeConfigParser

from Tkinter import *

protocols={socket.IPPROTO_TCP:'tcp',
	    socket.IPPROTO_UDP:'udp',
	    socket.IPPROTO_ICMP:'icmp'}

tcp_flags={0x01:'fin',
	   0x02:'syn',
	   0x04:'rst',
	   0x08:'push',
	   0x10:'ack',
	   0x20:'urg',
	   0x40:'ece',
	   0x80:'cwr'}

points = []
colors = {}
startttl = None
dumper = None
xmin = None
xmax = None
ymin = None
ymax = None
zmin = None
zmax = None
screenwidth = None
screenheight = None
config = None
proproot = None

def screenshot(filename=None):
    global screenwidth, screenheight

    try:
	#from PIL import Image
	import Image
    except:
	print "Screenshot capability requires the Python Image Library (PIL)."
	return

    width = screenwidth
    height = screenheight
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    img = Image.fromstring("RGB", (width, height), data)
    if filename:
	img.save(filename)
    else:
	# save based on timestamp
	pass


def decode_ethernet_frame(s):
    d={}

    # We want Ethernet II packets
    type=socket.ntohs(struct.unpack('H', s[12:14])[0])
    if type > 1500:
	d['type']='Ethernet II'
	d['ethernet_type']=s[12:14]
	d['data']=s[14:60]
	d['fcs']=s[60:64]

	# parse vlan information if this is a 802.1Q frame
	if type == 8100:
	    d['vlan_priority']=s[64:67]
	    d['vlan_cfi']=s[67:68]
	    d['vlan_vid']=s[68:80]

    return d

def decode_ip_packet(s):
    d={}
    d['version']=(ord(s[0]) & 0xf0) >> 4
    d['header_len']=ord(s[0]) & 0x0f
    d['tos']=ord(s[1])
    d['total_len']=socket.ntohs(struct.unpack('H',s[2:4])[0])
    d['id']=socket.ntohs(struct.unpack('H',s[4:6])[0])
    d['flags']=(ord(s[6]) & 0xe0) >> 5
    d['fragment_offset']=socket.ntohs(struct.unpack('H',s[6:8])[0] & 0x1f)
    d['ttl']=ord(s[8])
    d['protocol']=ord(s[9])
    d['checksum']=socket.ntohs(struct.unpack('H',s[10:12])[0])
    d['source_address']=socket.inet_ntoa(s[12:16])
    d['destination_address']=socket.inet_ntoa(s[16:20])
    if d['header_len']>5:
	d['options']=s[20:4*(d['header_len']-5)]
    else:
	d['options']=None
    d['data']=s[4*d['header_len']:]
    return d

def decode_tcp_packet(s):
    d={}
    #print "len=" + str(len(s))
    
    d['source_port']=socket.ntohs(struct.unpack('H', s[0:2])[0]) & 0xffff
    d['destination_port']=socket.ntohs(struct.unpack('H', s[2:4])[0]) & 0xffff
    d['sequence_number']=struct.unpack('I', s[4:8])[0]
    d['acknowledgement_number']=struct.unpack('I', s[8:12])[0]
    d['data_offset']=ord(s[12]) & 0xf0 >> 4
    d['reserved']=socket.ntohs(struct.unpack('H', s[12:14])[0]) & 0x0fc0 >> 6
    d['flags']=ord(s[13]) & 0x3f
    for k,v in tcp_flags.items():
	if (d['flags'] & k) > 0:
	    d[v] = 1
	else:
	    d[v] = 0
    d['window']=socket.ntohs(struct.unpack('H', s[14:16])[0])
    d['checksum']=socket.ntohs(struct.unpack('H', s[16:18])[0])
    d['urgent_pointer']=socket.ntohs(struct.unpack('H', s[18:20])[0])
    if len(s) > 20:
	d['options']=struct.unpack('I', s[20:24])[0] & 0x0fff
    if len(s) > 24:
	d['padding']=ord(s[24])
	d['data']=s[25:]

    return d

def decode_udp_packet(s):
    d={}
    
    d['source_port']=struct.unpack('H', s[1:3])[0]
    d['destination_port']=struct.unpack('H', s[3:5])[0]
    d['length']=struct.unpack('H', s[5:7])[0]
    d['checksum']=struct.unpack('H', s[7:9])[0]
    d['data']=s[9:]

    return d

def init():
    pygame.init()

    pygame.key.set_repeat(500, 30)
    
    pygame.display.set_caption("Cube Graphics")
    
#    glClearColor(0.0, 0.0, 0.0, 0.0)
#    glClearDepth(1.0)
#    glEnable(GL_BLEND)
#    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#    glDepthFunc(GL_LESS)
#    glEnable(GL_DEPTH_TEST)
#    glShadeModel(GL_SMOOTH)
#    glEnable(GL_LINE_SMOOTH)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
#    glLineWidth(linewidth)
#    glPointSize(pointsize)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def resize(width, height, fullscreen, linewidth, pointsize):
    #print "resizing to:  width=%s, height=%s, fullscreen=%s, type=%s" % (width, height, fullscreen, type(fullscreen))

    #mode = OPENGL | DOUBLEBUF | RESIZABLE
    mode = OPENGL | DOUBLEBUF
    if fullscreen:
	mode = mode | FULLSCREEN
	pygame.mouse.set_visible(0)
    else:
	mode = mode | RESIZABLE
	pygame.mouse.set_visible(1)

    pygame.display.set_mode((width, height), mode)

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LINE_SMOOTH)

    glLineWidth(linewidth)
    glPointSize(pointsize)

   
#def add_packet_point(pktlen, data, timestamp):
def add_packet_point(header, data):
    global startttl, dumper
    global xmin, xmax, ymin, ymax, zmin, zmax
    global config
   
    time_s, time_ms = header.getts()
    caplen = header.getcaplen() 

    if not data:
	return

    if dumper:
	dumper.dump(header, data)   
 
    #if data[12:14]=='\x08\x00':
    frame = decode_ethernet_frame(data)
    if frame['type'] == 'Ethernet II':
	if frame['ethernet_type'] == '\x08\x00':
	    packet = data[14:]
	elif frame['ethernet_type'] == '\x18\x00':
	    packet = data[16:]
	else:
	    return

	decoded=decode_ip_packet(packet)

	# TCP
	if decoded['protocol'] == socket.IPPROTO_TCP:
	    decoded['tcp_packet'] = decode_tcp_packet(decoded['data'])
	    port = (decoded['tcp_packet'])['destination_port']
	    if decoded['tcp_packet']['syn'] == 0 or decoded['tcp_packet']['ack'] == 1:
		return

	# UDP
	#elif decoded['protocol'] == socket.IPPROTO_UDP:
	    # for now, we only want tcp SYNs
	    
	    #decoded['udp_packet'] = decode_udp_packet(decoded['data'])
	    #port = (decoded['udp_packet'])['destination_port']

	else:
	    #print "IP packet protocol unrecognized."
	    return

	# x is destination
	# y is port
	# z is source
	source = socket.ntohl(struct.unpack('I',packet[12:16])[0])
	dest = socket.ntohl(struct.unpack('I',packet[16:20])[0])
	if source & 2**31:
            source = (source & (2**31-1)) + 2**31
        if dest & 2**31:
            dest = (dest & (2**31-1)) + 2**31

        #print "xmin=%d, xmax=%d, ymin=%d, ymax=%d, zmin=%d, zmax=%d" % (xmin, xmax, ymin, ymax, zmin, zmax)
        #print "x, y, z = %d, %d, %d" % (source, port, dest)
        if xmax == xmin:
            #print "xmax == xmin"
            x = 0.5
        else:
            #print "x = float(%d-%d)/float(%d-%d)" % (source, xmin, xmax, xmin)
            x = float(source-xmin)/float(xmax-xmin)

        if ymax == ymin:
            #print "ymax == ymin"
            y = 0.5
        else:
            #print "y = float(%d-%d)/float(%d-%d)" % (source, ymin, ymax, ymin)
            y = float(port-ymin)/float(ymax-ymin)

        if zmax == zmin:
            #print "zmax == zmin"
            z = 0.5
        else:
            #print "z = float(%d-%d)/float(%d-%d)" % (source, zmin, zmax, zmin)
            z = float(dest-zmin)/float(zmax-zmin)

 
	if x < 0.0 or x > 1.0 or y < 0.0 or y > 1.0 or z < 0.0 or z > 1.0:
 	    return

	lower, upper = 0.0, 1.0
	for k, v in colors.items():
	    if lower < k and k < y:
		lower = k
	    elif y < k and k < upper:
		upper = k
	lowcolor = colors[lower]
	highcolor = colors[upper]
	mod = (y - lower) / (upper - lower)
	r = lowcolor[0] + mod * (highcolor[0] - lowcolor[0])
	g = lowcolor[1] + mod * (highcolor[1] - lowcolor[1])
	b = lowcolor[2] + mod * (highcolor[2] - lowcolor[2])
	a = lowcolor[3] + mod * (highcolor[3] - lowcolor[3])

        startttl = config.getfloat('display', 'ttl')
        if startttl < 0:
            startttl = None
	points.append(((x, y, z), (r, g, b, a), startttl))

	#points.append(float(source)/float(2**32-1))
	#points.append(float(port)/float(2**16-1))
	#points.append(float(dest)/float(2**32-1))
  
def find_packager():
    frozen = getattr(sys, 'frozen', None) 
    if not frozen: 
	# COULD be certain cx_Freeze options or bundlebuilder, nothing to worry about though 
	return None 
    elif frozen in ('dll', 'console_exe', 'windows_exe'): 
	return 'py2exe' 
    elif frozen in ('macosx_app',): 
	return 'py2app' 
    elif frozen is True: 
	# it doesn't ALWAYS set this 
	return 'cx_Freeze' 
    else: 
	return '<unknown packager: %r>' % (frozen,)
 

def iprange(cidr):
    t = re.split("\/", cidr)
    range_mask = 2**32 - 2**(32-int(t[1]))
    ip = socket.ntohl(struct.unpack('I', socket.inet_aton(t[0]))[0])
    low = ip & range_mask
    high = ip | (range_mask ^ 2**32-1)
    return (low, high)
    

def listinterfaces(option, opt, value, parser):
    interfaces = pcapy.findalldevs()
    for index in range(len(interfaces)):
	print "%s => %s" % (index, interfaces[index])
    sys.exit()
 
def main(argv=None):
    global startttl, dumper
    global xcolor, ycolor, zcolor
    global xmin, xmax, ymin, ymax, zmin, zmax
    global config
    global proproot
    
    if argv is None:
	argv = sys.argv

    #tk = Tk()
    #tk.withdraw()
    
    import pkg_resources
    from ConfigParser import SafeConfigParser

    class MixedConfigParser(SafeConfigParser):
        """Reads a series of configuration files, updating the configuration
        with the settings in each subsequent file.  Useful for having a default
        configuration and overriding it with a user-specific configuration.
        """
	def read(self, filethings):
	    if isinstance(filethings, basestring) or isinstance(filethings, file):
		filethings = [filethings]
	    read_ok = []
	    for filething in filethings:
		try:
		    if isinstance(filething, file):
			fp = filething
			try:
			    filename = fp.name
			except AttributeError:
			    filename = '<???>'
		    else:
			fp = open(filething)
			filename = filething
		except IOError:
		    continue
		self._read(fp, filename)

    class TkinterConfigParser(MixedConfigParser):
        """Binds each configuration variable to a TK Variable so that updates to the variables are
        tracked and can be saved off from the configuration.  Also allows the configuration to be
        bound to a Tkinter UI.
        """
        def __init__(self):
            MixedConfigParser.__init__(self)
            #Tk()
            self.cfgvars = {}
	    self.vars = {}
	    self.callbacks = {}

        def read(self, filethings):
            MixedConfigParser.read(self, filethings)
            
            for sectionname in self.sections():
                if not self.callbacks.has_key(sectionname):
		    self.callbacks[sectionname] = {}
                #print " reading section: %s" % sectionname
                    
                for optionname in self.options(sectionname):
                    if not self.callbacks[sectionname].has_key(optionname):
			self.callbacks[sectionname][optionname] = []
                        #var = Variable()
			#var.section = sectionname
			#var.option = optionname
			#var.pending = False
			#print "adding trace: %s, %s, %s" % (var, sname, oname)
                        #self.cfgvars[sectionname][optionname] = var
			#self.vars[var._name] = var
			#f = lambda *args: self.var_cb(*args)
                        #var.trace('w', f)
                        
                    #val = self._sections[sectionname][optionname]
                    #print "     setting '%s' to '%s'" % (optionname, val)
                    #self.cfgvars[sectionname][optionname].set(val)

        def var_cb(self, var, varname, huh, event):
            """Called when a linked Variable is set.  Updates the core configuration with
            the new value."""

	    if self.vars.has_key(varname):
		var = self.vars[varname]

		section = var.section
		option = var.option

		if self.cfgvars.has_key(section) and self.cfgvars[section].has_key(option):
		    if not self.cfgvars[var.section][var.option].pending:
			self.cfgvars[var.section][var.option].pending = True
			self.set(var.section, var.option, var.get())
			self.cfgvars[var.section][var.option].pending = False
		else:
		    print "Error: received callback for variable '%s' but variable not found in config."
	    else:
		print "Error: received callback for variable '%s' but variable not found in config."


            
        def set(self, section, option, value):
            """Overrides MixedConfigParser.set() in order to update the linked Variable."""
            
            # Note: this set happens due to variable callback
            MixedConfigParser.set(self, section, option, value)
            if not self.callbacks.has_key(section):
		self.callbacks[section] = {}
                    

	    if self.cfgvars.has_key(section) and self.cfgvars[section].has_key(option):
		if not self.cfgvars[section][option].pending:
		    var = self.var_for(section, option)
		    var.pending = True
		    var.set(value)
		    var.pending = False

	    for cb in self.callbacks[section][option]:
		cb(section, option, value)

	def _ensurevar(self, section, option):
	    #print "checking for Variable: %s, %s" % (section, option)
	    if not self.cfgvars.has_key(section):
		#print "-> creating section: %s" % section
		self.cfgvars[section] = {}
	    options = self.cfgvars[section]
	    if not options.has_key(option):
		#print "-> creating option: %s" % option
		import Tkinter
		var = Tkinter.Variable()
		var.section = section
		var.option = option
		var.pending = False
                var.trace('w', lambda *args: self.var_cb(var, *args))

		self.vars[var._name] = var
		options[option] = var
		val = self._sections[section][option]
		#print "-> setting variable to: %s" % val
		var.set(val)

	def trace(self, section, option, callback):
	    if self.callbacks.has_key(section):
		options = self.callbacks[section]
		if options.has_key(option):
		    self.callbacks[section][option].append(callback)

	def var_for(self, section, option):
	    self._ensurevar(section, option)
	    return self.cfgvars[section][option]

    #tk = Tk()
    #tk.withdraw()
    #proproot = Tk()
    #proproot.withdraw()
    #config = MixedConfigParser()
    config = TkinterConfigParser()
    path = '~%s.netcube.cfg' % os.sep
    userfile = os.path.expanduser(path)
    f = open(userfile, 'r')
    config.read([pkg_resources.resource_stream(__name__, 'default.cfg'), f])
    #config.write(open('test.cfg', 'w'))
    #config.write(f)
    f.close()

    #proproot = None
    #import preferences
    #win = preferences.propsheet(master=proproot, config=config.cfgvars)
    #proproot.protocol('WM_DELETE_WINDOW', lambda wdw=proproot: Wm.withdraw(wdw))
    #win.pack()
    #win.mainloop()

    def setconfigoption(longopt, shortopt, cmdvalue, parser, config=None, section=None, option=None, value=None):
	if value:
	    cmdvalue = value
	#print "%s, %s, %s, %s" % (config, section, option, cmdvalue)
	if config is not None and section is not None and option is not None and cmdvalue is not None:
	    config.set(section, option, str(cmdvalue))

	else:
	    print "Not enough info for option: config=%s, section=%s, option=%s, cmdvalue=%s" % (config, section, option, cmdvalue)
    
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-i", "--interface", help="read packets from INTERFACE", metavar="INTERFACE", type='string',
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section' : 'capture', 'option' : 'interface'})
    parser.add_option('-l', '--list', action='callback', callback=listinterfaces)
    parser.add_option("-f", "--fullscreen", help="display in fullscreen mode",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section' : 'display', 'option' : 'fullscreen', 'value' : True})
    parser.add_option("-p", "--promisc", help="put the interface into promiscuous mode",
	    action="callback", callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'capture', 'option': 'promisc', 'value' : True})
    parser.add_option("-P", "--nopromisc", dest="promisc", help="DO NOT put the interface into promiscuous mode",
	    action="callback", callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'capture', 'option': 'promisc', 'value' : False})
    parser.add_option("-r", "--read", dest="readfile", help="read packets previously captured to FILE", metavar="FILE",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'capture', 'option': 'read'})
    parser.add_option("-w", "--write", dest="writefile", help="write packets to FILE", metavar="FILE",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'capture', 'option': 'write'})
    parser.add_option("--filter", dest="filter", help="filter captured packets using FILTER", metavar="FILTER",
	    default='tcp[tcpflags] == tcp-syn', action='callback', callback=setconfigoption, 
	    callback_kwargs={'config' : config, 'section': 'capture', 'option': 'filter'})
    parser.add_option("--pointsize", dest="pointsize", help="set the point size to SIZE pixels", metavar="SIZE", default=1.0, type="float",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'pointsize'})
    parser.add_option("--linewidth", dest="linewidth", help="set the line width to WIDTH pixels", metavar="WIDTH", default=1.0, type="float",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'linewidth'})
    parser.add_option("--fps", dest="fps", help="attempt to display FRAMES frames per second", metavar="FRAMES", default=30, type="int",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'fps'})
    parser.add_option("--width", dest="width", help="set display width to WIDTH pixels", metavar="WIDTH", default=320, type="int",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'width'})
    parser.add_option("--height", dest="height", help="set display height to HEIGHT pixels", metavar="HEIGHT", default=240, type="int",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'height'})
    parser.add_option("-c", "--colors", dest="colors", help="set the vertical gradient colors", metavar="'<y,r,g,b,a> [ ...]'",
	    default="0.0,1.0,0.0,0.0,1.0 0.5,0.0,1.0,0.0,1.0 1.0,0.0,0.0,1.0,1.0",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'colors'})
    parser.add_option("-t", "--ttl", dest="ttl", help="set the lifetime of packet points (in seconds)", default=None, type="float",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'ttl'})
    parser.add_option("--xcolor", dest="xcolor", help="set the x-axis color", metavar="r,g,b,a", default="0.5,0.0,0.0,0.5",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'xcolor'})
    parser.add_option("--ycolor", dest="ycolor", help="set the y-axis color", metavar="r,g,b,a", default="0.0,0.5,0.0,0.5",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'ycolor'})
    parser.add_option("--zcolor", dest="zcolor", help="set the z-axis color", metavar="r,g,b,a", default="0.0,0.0,0.5,0.5",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'zcolor'})
    parser.add_option("-s", "--spin", dest="spin", help="set the spin rate in degrees / second", default=10.0, type="float",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'spin'})
    parser.add_option("--xmin", dest="xmin", help="x axis minimum address", metavar="a.b.c.d", default="0.0.0.0",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'xmin'})
    parser.add_option("--xmax", dest="xmax", help="x axis maximum address", metavar="a.b.c.d", default="255.255.255.255",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'xmax'})
    parser.add_option("--ymin", dest="ymin", help="y axis minimum port", metavar="x", default=0, type="int",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'ymin'})
    parser.add_option("--ymax", dest="ymax", help="y axis maximum port", metavar="x", default=65535, type="int",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'ymax'})
    parser.add_option("--zmin", dest="zmin", help="z axis minimum address", metavar="a.b.c.d", default="0.0.0.0",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'zmin'})
    parser.add_option("--zmax", dest="zmax", help="z axis maximum address", metavar="a.b.c.d", default="255.255.255.255",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'zmax'})
    parser.add_option("--xcidrip", dest="xcidrip", help="x axis network range in CIDR (IP)", metavar="a.b.c.d",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'xcidrip'})
    parser.add_option("--xcidrmask", dest="xcidrmask", help="x axis network range in CIDR (mask)", metavar="x",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'xcidrmask'})
    parser.add_option("--zcidrip", dest="zcidrip", help="z axis network range in CIDR (IP)", metavar="a.b.c.d",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'zcidrip'})
    parser.add_option("--zcidrmask", dest="zcidrmask", help="z axis network range in CIDR (mask)", metavar="z",
	    action='callback', callback=setconfigoption,
	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'zcidrmask'})
    parser.add_option("--xbounds", dest="xbounds", help="x axis bounds type (range, cidr, device)",
            action='callback', callback=setconfigoption,
            callback_kwargs={'config' : config, 'section': 'display', 'option': 'xbounds'})
    parser.add_option("--zbounds", dest="xbounds", help="z axis bounds type (range, cidr, device)",
            action='callback', callback=setconfigoption,
            callback_kwargs={'config' : config, 'section': 'display', 'option': 'zbounds'})
#    parser.add_option("--xusedevrange", dest="xusedevrange", help="get x axis range from network device",
#	    action='callback', callback=setconfigoption,
#	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'xusedevrange', 'value' : True})
#    parser.add_option("--zusedevrange", dest="zusedevrange", help="get z axis range from network device",
#	    action='callback', callback=setconfigoption,
#	    callback_kwargs={'config' : config, 'section': 'display', 'option': 'zusedevrange', 'value' : True})

    options, args = parser.parse_args(argv[1:])


    def updatelinewidth(section, option, value):
	linewidth = value
	glLineWidth(float(linewidth))

    def updatepointsize(section, option, value):
	pointsize = value
	glPointSize(float(pointsize))

    #config.cfgvars['display']['linewidth'].trace('w', updatelinewidth)
    #config.cfgvars['display']['pointsize'].trace('w', updatepointsize)
    config.trace('display', 'linewidth', updatelinewidth)
    config.trace('display', 'pointsize', updatepointsize)

    def updatefullscreen(section, option, value):
	width = config.getint('display', 'width')
	height = config.getint('display', 'height')
	linewidth = config.getint('display', 'linewidth')
	pointsize = config.getint('display', 'pointsize')
	fullscreen = config.getboolean('display', 'fullscreen')
	resize(width, height, fullscreen, linewidth, pointsize)
	

    #config.cfgvars['display']['fullscreen'].trace('w', lambda *args: updatefullscreen(*args))
    config.trace('display', 'fullscreen', updatefullscreen)


    def updateframesize(event):
	height = config.getint('display', 'height')
	width = config.getint('display', 'width')
	#print "resizing with:  width=%s, height=%s" % (width, height)
	fullscreen = config.getboolean('display', 'fullscreen')
	linewidth = config.getint('display', 'linewidth')
	pointsize = config.getint('display', 'pointsize')
	resize(width, height, fullscreen, linewidth, pointsize)

    #win.displaysettings.col1.screen.resolution.width.bind("<FocusOut>", updateframesize)
    #win.displaysettings.col1.screen.resolution.height.bind("<FocusOut>", updateframesize)




    interfaces = pcapy.findalldevs()
    if config.has_option('capture', 'interface') and len(config.get('capture', 'interface')) > 0:
	interface = config.get('capture', 'interface')

	# See if that's a valid interface
	try:
	    interfaces.index(interface)
	except ValueError:
	    # Nope!  Let's see if it's a number index
	    try:
		index = int(interface)
	    except ValueError:
		# Nope!
		print "Interface specified doesn't exist!"
		return

	    # Conversion was successful, let's try it
	    if index >= 0 and index < len(interfaces):
		interface = interfaces[index]
    else:
	interface = pcapy.lookupdev()

    print "Using interface %s" % interface
    
    #promisc = config.getboolean('capture', 'promisc')
    #readfile = config.get('capture', 'read')
    #writefile = config.get('capture', 'write')
    #pointsize = config.getfloat('display', 'pointsize')
    #linewidth = config.getfloat('display', 'linewidth')
    #fullscreen = config.getboolean('display', 'fullscreen')
    #desiredframes = config.getfloat('display', 'fps')
    #width = config.getint('display', 'width')
    #height = config.getint('display', 'height')
    #colorlist = config.get('display', 'colors')
    #startttl = config.getfloat('display', 'ttl')
    #if startttl < 0:
    #	startttl = None
    #rate = config.getfloat('display', 'spin')
    #xcolor = config.get('display', 'xcolor')
    #ycolor = config.get('display', 'ycolor')
    #zcolor = config.get('display', 'zcolor')
    #if len(args) > 0:
    #	filter = string.join(args)
    #else:
    #	filter = "tcp[tcpflags] == tcp-syn"
	


    ymin = config.getint('display', 'ymin')
    ymax = config.getint('display', 'ymax')

    #xrange = config.get('display', 'xrange')
    #zrange = config.get('display', 'zrange')    
    #if xrange:
    #	xmin, xmax = iprange(xrange)

    #if zrange:
    #	zmin, zmax = iprange(zrange) 

    # Note that xmax and zmax checks are delayed for xusedevrange and zusedevrange

    #xusedevrange = config.has_option('display', 'xusedevrange') and config.get('display', 'xusedevrange')
    #zusedevrange = config.has_option('display', 'zusedevrange') and config.get('display', 'zusedevrange')


    #xcolor = config.get('display', 'xcolor')
    #r, g, b, a = string.split(xcolor, ",")
    #xcolor = (float(r), float(g), float(b), float(a))
    
    #ycolor = config.get('display', 'ycolor')
    #r, g, b, a = string.split(ycolor, ",")
    #ycolor = (float(r), float(g), float(b), float(a))

    #zcolor = config.get('display', 'zcolor')
    #r, g, b, a = string.split(zcolor, ",")
    #zcolor = (float(r), float(g), float(b), float(a))

    colorlist = config.get('display', 'colors')
    for entry in string.split(colorlist):
	y, r, g, b, a = string.split(entry, ",")
	colors[float(y)] = (float(r), float(g), float(b), float(a))
 




    # Initialize networking
    p = None
    readfile = config.get('capture', 'read')
    if readfile:
	p = pcapy.open_offline(readfile)
    else:
        promisc = config.getboolean('capture', 'promisc')
	p = pcapy.open_live(interface, 68, promisc, 100)
	
    net = p.getnet()
    mask = p.getmask()


    
    xbounds = config.has_option('display', 'xbounds') and config.get('display', 'xbounds')
    zbounds = config.has_option('display', 'zbounds') and config.get('display', 'zbounds')

    # Pepare the X axis min and max.
    if xbounds == 'range':
        xmin = struct.unpack('I', socket.inet_aton(config.get('display', 'xmin')))[0]
        if config.get('display', 'xmax') is "255.255.255.255":
            xmax = 2**32-1
        else:
            xmax = struct.unpack('I', socket.inet_aton(config.get('display', 'xmax')))[0]
    elif xbounds == 'cidr':
	xcidrip = config.get('display', 'xcidrip')
	xcidrmask = config.get('display', 'xcidrmask')
        xmin, xmax = iprange("%s/%s" % (xcidrip, xcidrmask))
    else:
        try:
            mask_n = socket.ntohl(struct.unpack('I', socket.inet_aton(mask))[0])
            if mask_n & 2**31:
                mask_n = mask_n & (2**31-1) + 2**31
        except:
            mask_n = 2**32 - 1

        n = 0
        while mask_n > 0:
            mask_n = (mask_n << 1) & (2**32 - 1)
            n += 1
        
        cidr = net + "/" + str(n)
        xmin, xmax = iprange(cidr)

    # Pepare the Z axis min and max.
    if zbounds == 'range':
        zmin = struct.unpack('I', socket.inet_aton(config.get('display', 'zmin')))[0]
        if config.get('display', 'zmax') is "255.255.255.255":
            zmax = 2**32-1
        else:
            zmax = struct.unpack('I', socket.inet_aton(config.get('display', 'zmax')))[0]
    elif zbounds == 'cidr':
	zcidrip = config.get('display', 'zcidrip')
	zcidrmask = config.get('display', 'zcidrmask')
        zmin, zmax = iprange("%s/%s" % (zcidrip, zcidrmask))
    else:
        try:
            mask_n = socket.ntohl(struct.unpack('I', socket.inet_aton(mask))[0])
            if mask_n & 2**31:
                mask_n = mask_n & (2**31-1) + 2**31
        except:
            mask_n = 2**32 - 1

        n = 0
        while mask_n > 0:
            mask_n = (mask_n << 1) & (2**32 - 1)
            n += 1
        
        cidr = net + "/" + str(n)
        zmin, zmax = iprange(cidr)
        

    if xmax & 2**31:
        xmax = (xmax & (2**31-1)) + 2**31

    if zmax & 2**31:
        zmax = (zmax & (2**31-1)) + 2**31

    filter = config.get('capture', 'filter')
    #if filter is not None:
    #	p.setfilter(filter)
    if filter is not None:
	try:
	    p.setfilter(filter)
	except pcapy.PcapError, e:
	    print "Invalid filter: %s" % v

    def updatefilter(s, o, v):
	try:
	    p.setfilter(v)
	except pcapy.PcapError, e:
	    print "Invalid filter: %s" % v

    config.trace('capture', 'filter', updatefilter)

    writefile = config.get('capture', 'write')
    if writefile:
	dumper = p.dump_open(writefile)

    p.setnonblock(1)


    # Initialize graphics
    pointsize = config.getfloat('display', 'pointsize')
    linewidth = config.getfloat('display', 'linewidth')
    fullscreen = config.getboolean('display', 'fullscreen')
    width = config.getint('display', 'width')
    height = config.getint('display', 'height')
    init()
    resize(width, height, fullscreen, linewidth, pointsize)
    updatelinewidth(None, None, linewidth)

    rotation = 0.0
    frames = 0
    clock = pygame.time.Clock()

    ticks = startticks = pygame.time.get_ticks()
    saverate = None    

    control_mask = KMOD_SHIFT | KMOD_CTRL | KMOD_ALT | KMOD_META

    while 1:
        # Let Tkinter do its thing:
        #tk.update()
	if not proproot == None:
	    proproot.update()
        
	event = pygame.event.poll()
	#events = pygame.event.get()
	#for event in events:
	if event is not None:
	    if event.type == pygame.VIDEORESIZE:
		#print "resize! event=%s" % event.h
		config.set('display', 'width', str(event.w))
		config.set('display', 'height', str(event.h))
		fullscreen = config.getboolean('display', 'fullscreen')
		#resize(event.w, event.h, fullscreen)

	    elif event.type == KEYDOWN:         
		if event.key == K_f:
		    fullscreen = config.getboolean('display', 'fullscreen')
		    if fullscreen:
			fullscreen = False
		    else:
			fullscreen = True
		    config.set('display', 'fullscreen', str(fullscreen))
		    #width = config.getint('display', 'width')
		    #height = config.getint('display', 'height')
		    #resize(width, height, fullscreen)
		if event.key == K_s:
		    if saverate:
			rate = saverate
			saverate = None
		    else:
			saverate = rate
			rate = 0.0
		elif event.key == K_p:
		    screenshot("screen.png")
		elif event.key == K_c:
		    if proproot == None:
			import preferences
			proproot = Tk()
			proproot.withdraw()
			proproot.title('NetCube Preferences')
			proproot.win = preferences.propsheet(master=proproot, config=config, width=327)
			proproot.win.screen.resolution.width.bind("<FocusOut>", updateframesize)
			proproot.win.screen.resolution.height.bind("<FocusOut>", updateframesize)
			proproot.protocol('WM_DELETE_WINDOW', lambda wdw=proproot: Wm.withdraw(wdw))
			proproot.win.pack(expand=1, fill=BOTH)
			proproot.deiconify()
		    else:
			if proproot.state() == 'withdrawn':
			    proproot.deiconify()
			else:
			    proproot.withdraw()
		elif event.key == K_EQUALS or event.key == K_KP_PLUS:
		    if event.mod & control_mask & KMOD_SHIFT:
			mod = 0.1
		    elif event.mod & control_mask & KMOD_CTRL:
			mod = 10.0
		    else:
			mod = 1.0
			
		    if saverate:
			rotation += mod % 360
		    else:
			rate += mod
		elif event.key == K_MINUS or event.key == K_KP_MINUS:
		    if event.mod & control_mask & KMOD_SHIFT:
			mod = -0.1
		    elif event.mod & control_mask & KMOD_CTRL:
			mod = -10.0
		    else:
			mod = -1.0
			
		    if saverate:
			rotation += mod % 360
		    else:
			rate += mod
		#elif event.key == K_ESCAPE:
		#    fullscreen = config.getboolean('display', 'fullscreen')
		#    if fullscreen:
		#	print "in escape 1, fullscreen=%s" % fullscreen
		#	fullscreen = False
		#	config.set('display', 'fullscreen', str(fullscreen))
		#	print "in escape 2, fullscreen=%s" % fullscreen
		#    else:
		#	print "breaking"
		#	break
		
	    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
		break

	try:
	    p.dispatch(0, add_packet_point)
	except Exception, msg:
	    print "p.dispatch() got exception:", Exception, msg

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()

	glTranslatef(0.0, 0.0, -2.0)
	glRotate(rotation, 0.0, 1.0, 0.0)
	glTranslatef(-0.5, -0.5, -0.5)

	oticks = ticks
	ticks = pygame.time.get_ticks()
	newrate = config.getfloat('display', 'spin')
	if saverate is not None:
            saverate = newrate
        else:
            rate = newrate
	rotation += rate * (ticks-oticks) / 1000.0
	rotation = rotation % 360

        # Render points first so that axes get alpha blended.
	glBegin(GL_POINTS)
	adj = 0
	for i in range(0, len(points)):
	    j = i - adj
	    #x, y, z = points[i:i+3]
	    #r, g, b = 0.125, 0.25 + y * 0.5, 0.125
	    point, color, ttl = points[j]
	    if ttl:
		if ttl < 0.0:
		    points[j:j+1] = []
		    adj += 1
		else:
		    points[j] = (point, color, ttl-float(ticks - oticks)/1000.0)
	    x, y, z = point
	    r, g, b, a = color
	    glColor4f(r, g, b, a)
	    glVertex3f(x, y, z)
	glEnd()


        xcolor = config.get('display', 'xcolor')
        r, g, b, a = string.split(xcolor, ",")
        xcolor = (float(r), float(g), float(b), float(a))

	#print "drawing lines, xcolor=%s, %s, %s, %s" % (xcolor)

	glBegin(GL_LINES)
	r, g, b, a = xcolor
	glColor4f(r, g, b, a)
	glVertex3f(0.0, 0.0, 0.0)
	glVertex3f(1.0, 0.0, 0.0)
	glVertex3f(0.0, 0.0, 1.0)
	glVertex3f(1.0, 0.0, 1.0)
	glVertex3f(0.0, 1.0, 0.0)
	glVertex3f(1.0, 1.0, 0.0)
	glVertex3f(0.0, 1.0, 1.0)
	glVertex3f(1.0, 1.0, 1.0)



        zcolor = config.get('display', 'zcolor')
        r, g, b, a = string.split(zcolor, ",")
        zcolor = (float(r), float(g), float(b), float(a))

	r, g, b, a = zcolor
	glColor4f(r, g, b, a)
	glVertex3f(0.0, 0.0, 0.0)
	glVertex3f(0.0, 0.0, 1.0)
	glVertex3f(1.0, 0.0, 0.0)
	glVertex3f(1.0, 0.0, 1.0)
	glVertex3f(0.0, 1.0, 0.0)
	glVertex3f(0.0, 1.0, 1.0)
	glVertex3f(1.0, 1.0, 0.0)
	glVertex3f(1.0, 1.0, 1.0)



           
        ycolor = config.get('display', 'ycolor')
        r, g, b, a = string.split(ycolor, ",")
        ycolor = (float(r), float(g), float(b), float(a))
	r, g, b, a = ycolor
	glColor4f(r, g, b, a)
	glVertex3f(0.0, 0.0, 0.0)
	glVertex3f(0.0, 1.0, 0.0)
	glVertex3f(1.0, 0.0, 0.0)
	glVertex3f(1.0, 1.0, 0.0)
	glVertex3f(0.0, 0.0, 1.0)
	glVertex3f(0.0, 1.0, 1.0)
	glVertex3f(1.0, 0.0, 1.0)
	glVertex3f(1.0, 1.0, 1.0)
	glEnd()


	
	glLoadIdentity()

	pygame.display.flip()

	#frames = frames + 1

        desiredframes = config.getfloat('display', 'fps')
	clock.tick(desiredframes)

    #print "fps:  %d" % ((frames * 1000) / (pygame.time.get_ticks() - startticks))
    #file = os.path.expanduser('~/.netcube.cfg'))
    f = open(userfile, 'w')
    config.write(f)
    f.close()

if __name__ == "__main__":
    sys.exit(main())
    
