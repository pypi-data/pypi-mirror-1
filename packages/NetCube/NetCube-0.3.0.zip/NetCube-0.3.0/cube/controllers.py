#!/usr/bin/env python

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

import config
import network
import pkg_resources
import optparse
import scenegraph
import display
import graphics
import struct
import socket

import time

# used for animating rotation (which should be moved to the scenegraph or similar as animators)
import pygame
from pygame.locals import *

# used for preferences dialog from PygameEventController
from Tkinter import *

class QuitEvent(Exception):
    pass

class Controller:
    """An 'abstract' controlling class used to manage a particular aspect of
    the NetCube."""
    def __init__(self, config, section):
	"""Initialize this controller, using config as the source of
	configuration options for the controller and section as the name of a
	section in the configuration from which to read configuration
	options.""" 
	pass

    def run(self):
	"""Run this Controller through one iteration of processing.  This
	should give up control in order for the main loop / controller to
	continue to process other controllers as well."""
	pass

class NetworkController(Controller):
    """A controller that manages incoming pcapy packet data, transforms it into
    data that can be used by a grapher, and hands it off to such a grapher.
    This grapher should be set in order for data to be displayed otherwise this
    controller does not save captured data."""

    def __init__(self, config, section='capture'):
	"""Initialize the NetworkController.  Uses a configuration section to
	read these values:

	    interface:	    the network interface from which to grab packets.
	    promiscuous:    whether to capture packets promiscuously.
	    filter:	    the pcap filter to use while capturing packets.
	    read:	    a pcap capture file from which to read packets.
	    write:	    a pcap capture file to which to write packets.

	Somehow this class should provide for the listing of interfaces as
	triggered by the command line switch '-l'.
	"""
	self.config = config
	self.readfile = config.get(section, 'read')
	self.writefile = config.get(section, 'write')
	self.promisc = config.getboolean(section, 'promisc')
	self.interface = config.get(section, 'interface')

	self.reader = network.PacketReader(readfile=self.readfile, promisc=self.promisc, interface=self.interface, nonblock=1)
	self.reader.setup()

	self.parser = network.ParsedPacketReader(self.reader)

    def run(self):
	"""Check the pcapy source for new packets.  As they are found, parse
	them and add the resulting data to the graphics destination."""

	packets = self.parser.read()
	for packet in packets:
	    self.grapher.data.append(packet)

class DisplayController(Controller):
    def __init__(self, config, section='display'):
	display.init()
	height = config.getint(section, 'height')
	width = config.getint(section, 'width')
	fullscreen = config.getboolean(section, 'fullscreen')
	linewidth = config.getint(section, 'linewidth')
	pointsize = config.getint(section, 'pointsize')

	display.resize(width, height, fullscreen, linewidth, pointsize)
	
	self.config = config
	self.config.trace(section, 'linewidth', self.updatelinewidth)
	self.config.trace(section, 'pointsize', self.updatepointsize)
	self.config.trace(section, 'fullscreen', self.updatefullscreen)

    def updatelinewidth(self, section, option, value):
	display.updatelinewidth(value)

    def updatepointsize(self, section, option, value):
	display.updatepointsize(value)

    def updatefullscreen(self, section, option, value):
	width = self.config.getint('display', 'width')
	height = self.config.getint('display', 'height')
	linewidth = self.config.getint('display', 'linewidth')
	pointsize = self.config.getint('display', 'pointsize')
	fullscreen = self.config.getboolean('display', 'fullscreen')
	display.resize(width, height, fullscreen, linewidth, pointsize)



class GraphicsController(Controller):
    def axiscolor_to_tuple(self, colorstr):
	r, g, b, a = [float(x) for x in colorstr.split(',')]
	return (r, g, b, a)

    def linewidth_cb(self, section, option, value):
	self.lwframe.fromwidth = int(value)

    def __init__(self, config, section='graphics'):
	self.config = config


	# Set up the point grapher
	self.grapher = graphics.NetworkCube()
	if self.config.has_option(section, 'optimize'):
	    self.grapher.optimize = config.getint(section, 'optimize')
	else:
	    self.grapher.optimize = 0

	self.grapher.pushTranslation(-0.5, -0.5, -0.5)
	self.grapher.pushColor(0.75, 0.75, 0.75)
	
	# Set the axis colors
	colorlist = config.get(section, 'colors')
	for entry in colorlist.split():
	    y, r, g, b, a = entry.split(',')
	    self.grapher.colors[float(y)] = (float(r), float(g),
		    float(b), float(a))

	self.grapher.xcolor = self.axiscolor_to_tuple(config.get(section, 'xcolor'))
	self.grapher.ycolor = self.axiscolor_to_tuple(config.get(section, 'ycolor'))
	self.grapher.zcolor = self.axiscolor_to_tuple(config.get(section, 'zcolor'))

	config.trace(section, 'xcolor', self.axiscolor_cb)
	config.trace(section, 'ycolor', self.axiscolor_cb)
	config.trace(section, 'zcolor', self.axiscolor_cb)
	
	# Set the axis minumums and maximums
	self.grapher.ymin = config.getint(section, 'ymin')
	self.grapher.ymax = config.getint(section, 'ymax')
	
	xbounds = config.has_option(section, 'xbounds') and config.get(section, 'xbounds')
	zbounds = config.has_option(section, 'zbounds') and config.get(section, 'zbounds') 



	# Pepare the X axis min and max.
	if xbounds == 'range':
	    self.grapher.xmin = struct.unpack('I', socket.inet_aton(config.get(section, 'xmin')))[0]
	    if config.get(section, 'xmax') is "255.255.255.255":
		self.grapher.xmax = 2**32-1
	    else:
		self.grapher.xmax = struct.unpack('I', socket.inet_aton(config.get(section, 'xmax')))[0]
	elif xbounds == 'cidr':
	    xcidrip = config.get(section, 'xcidrip')
	    xcidrmask = config.get(section, 'xcidrmask')
	    self.grapher.xmin, self.grapher.xmax = network.iprange("%s/%s" % (xcidrip, xcidrmask))
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
	    self.grapher.xmin, self.grapher.xmax = network.iprange(cidr)

	# Pepare the Z axis min and max.
	if zbounds == 'range':
	    self.grapher.zmin = struct.unpack('I', socket.inet_aton(config.get(section, 'zmin')))[0]
	    if config.get(section, 'zmax') is "255.255.255.255":
		self.grapher.zmax = 2**32-1
	    else:
		self.grapher.zmax = struct.unpack('I', socket.inet_aton(config.get(section, 'zmax')))[0]
	elif zbounds == 'cidr':
	    zcidrip = config.get(section, 'zcidrip')
	    zcidrmask = config.get(section, 'zcidrmask')
	    self.grapher.zmin, self.grapher.zmax = network.iprange("%s/%s" % (zcidrip, zcidrmask))
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
	    self.grapher.zmin, self.grapher.zmax = network.iprange(cidr)
	    

	if self.grapher.xmax & 2**31:
	    self.grapher.xmax = (self.grapher.xmax & (2**31-1)) + 2**31

	if self.grapher.zmax & 2**31:
	    self.grapher.zmax = (self.grapher.zmax & (2**31-1)) + 2**31



	# Set up our main frame of reference
	self.context = scenegraph.GLFrame()
	self.context.pushTransform(scenegraph.Identity())
	self.context.pushTranslation(0.0, 0.0, -2.0)
	self.rotation = scenegraph.Rotation(0.0, 0.0, 1.0, 0.0)
	self.context.pushTransform(self.rotation)




	# Add axis label objects



	self.labelcontext = scenegraph.BlackoutFrame(lambda: self.axislabels)
	self.lwframe = scenegraph.LineWidthFrame(self.config.getint('display', 'linewidth'), 1)
	self.config.trace('display', 'linewidth', self.linewidth_cb)
	self.labelcontext.children.append(self.lwframe)

	self.context.children.append(self.labelcontext)

	self.xlabel = scenegraph.StrokeText('Source', font=scenegraph.GLUT_STROKE_ROMAN, align=scenegraph.CENTER)
	self.xlabel.pushTranslation(0.0, -0.6, -0.6)
	self.ylabel = scenegraph.StrokeText('Port', font=scenegraph.GLUT_STROKE_ROMAN, align=scenegraph.CENTER)
	self.ylabel.pushTranslation(-0.6, 0.0, -0.6)
	self.zlabel = scenegraph.StrokeText('Destination', font=scenegraph.GLUT_STROKE_ROMAN, align=scenegraph.CENTER)
	self.zlabel.pushTranslation(-0.6, -0.6, 0.0)

	self.xminlabel = scenegraph.StrokeText(network.int_to_dottedquad(self.grapher.xmin), align=scenegraph.CENTER)
	self.xminlabel.pushTranslation(-0.5, -0.6, -0.6)
	self.xmaxlabel = scenegraph.StrokeText(network.int_to_dottedquad(self.grapher.xmax), align=scenegraph.CENTER)
	self.xmaxlabel.pushTranslation(0.5, -0.6, -0.6)

	self.yminlabel = scenegraph.StrokeText(str(self.grapher.ymin), align=scenegraph.CENTER)
	self.yminlabel.pushTranslation(-0.6, -0.5, -0.6)
	self.ymaxlabel = scenegraph.StrokeText(str(self.grapher.ymax), align=scenegraph.CENTER)
	self.ymaxlabel.pushTranslation(-0.6, 0.5, -0.6)

	self.zminlabel = scenegraph.StrokeText(network.int_to_dottedquad(self.grapher.zmin), align=scenegraph.CENTER)
	self.zminlabel.pushTranslation(-0.6, -0.6, -0.5)
	self.zmaxlabel = scenegraph.StrokeText(network.int_to_dottedquad(self.grapher.zmax), align=scenegraph.CENTER)
	self.zmaxlabel.pushTranslation(-0.6, -0.6, 0.5)


	for el in [self.xlabel, self.ylabel, self.zlabel, self.xminlabel, self.yminlabel, self.zminlabel, self.xmaxlabel, self.ymaxlabel, self.zmaxlabel]:
	    el.pushScale(0.0005, 0.0005, 0.0005)
	    self.orotation = scenegraph.InverseRotation(self.rotation)
	    el.pushTransform(self.orotation)
	    el.pushColor(0.4, 0.4, 0.4, 1.0)
	    self.lwframe.children.append(el)


	# Set traces on important config variables
	config.trace(section, 'spin', self.spin_cb)
	self.spinrate = config.getint(section, 'spin')

	config.trace(section, 'axislabels', self.axislabels_cb)
	self.axislabels = config.getboolean(section, 'axislabels')

	# initialize animation counters
	self.oticks = self.ticks = pygame.time.get_ticks()


	# Add the grapher to the context
	self.context.children.append(self.grapher)

    def spin_cb(self, section, option, value):
	self.spinrate = int(value)

    def axislabels_cb(self, section, option, value):
	self.axislabels = bool(int(value))

    def axiscolor_cb(self, section, option, value):
	value = self.axiscolor_to_tuple(value)
	if option == 'xcolor':
	    self.grapher.xcolor = value
	elif option == 'ycolor':
	    self.grapher.ycolor = value
	elif option == 'zcolor':
	    self.grapher.zcolor = value


    def run(self):
	display.clear()

	self.oticks = self.ticks
	self.ticks = pygame.time.get_ticks()
	self.rotation.r += self.spinrate * (self.ticks-self.oticks) / 1000.0
	self.rotation.r %= 360

	
	self.context.render()
	#print "tick delta=%s, datasize=%s" % (pygame.time.get_ticks() - self.ticks, len(self.grapher.data))
	display.flip()

class ConfigurationController(Controller):
    """A controller that manages configuration data."""

    def __init__(self, argv=None):
	"""Initialize the ConfigurationController."""
	import os
	import sys

	if argv is None:
	    argv = sys.argv

	self.parser = config.TkinterConfigParser()
	path = '~%s.netcube.cfg' % os.sep
	self.userfile = os.path.expanduser(path)

	files = [pkg_resources.resource_stream(__name__, 'default.cfg')]
	f = None
	if os.path.exists(self.userfile):
	    f = open(self.userfile, 'r')
	    files.append(f)
	self.parser.read(files)
	if f is not None:
	    f.close()

	op = optparse.OptionParser("usage: %prog [options]\n\nPress the 'c' key to open a configuration dialog while the program is running.")
	op.add_option("-i", "--interface", help="read packets from INTERFACE",
		metavar="INTERFACE", type='string', action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section' : 'capture', 'option' : 'interface'})
	op.add_option('-l', '--list', action='callback', callback=self.listinterfaces)
	op.add_option("-f", "--fullscreen", help="display in fullscreen mode",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section' : 'display',
		'option' : 'fullscreen', 'value' : True})
	op.add_option("-p", "--promisc", help="put the interface into promiscuous mode",
		action="callback", callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'capture',
		'option': 'promisc', 'value' : True})
	op.add_option("-P", "--nopromisc", dest="promisc",
		help="DO NOT put the interface into promiscuous mode", action="callback",
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'capture', 'option': 'promisc', 'value' : False})
	op.add_option("-a", "--axislabels", help="show axis labels",
		action="callback", callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'axislabels', 'value' : 1})
	op.add_option("-A", "--noaxislabels", dest="axislabels",
		help="DO NOT show axis labels", action="callback",
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'axislabels', 'value' : 0})
	op.add_option("-r", "--read", dest="readfile",
		help="read packets previously captured to FILE", metavar="FILE",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'capture', 'option': 'read'})
	op.add_option("-w", "--write", dest="writefile",
		help="write packets to FILE", metavar="FILE", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'capture', 'option': 'write'})
	op.add_option("--filter", dest="netfilter",
		help="filter captured packets using FILTER", metavar="FILTER",
		default='tcp[tcpflags] == tcp-syn', action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'capture',
		'option': 'filter'})
	op.add_option("--pointsize", dest="pointsize",
		help="set the point size to SIZE pixels", metavar="SIZE", default=1.0, type="float",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'display',
		'option': 'pointsize'})
	op.add_option("--linewidth", dest="linewidth",
		help="set the line width to WIDTH pixels", metavar="WIDTH", default=1.0, type="float",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'display',
		'option': 'linewidth'})
	op.add_option("--fps", dest="fps",
		help="attempt to display FRAMES frames per second", metavar="FRAMES", default=30, type="int",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'display',
		'option': 'fps'})
	op.add_option("--width", dest="width",
		help="set display width to WIDTH pixels", metavar="WIDTH", default=320, type="int",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'display',
		'option': 'width'})
	op.add_option("--height", dest="height",
		help="set display height to HEIGHT pixels", metavar="HEIGHT", default=240, type="int",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'display',
		'option': 'height'})
	op.add_option("-c", "--colors", dest="colors",
		help="set the vertical gradient colors", metavar="'<y,r,g,b,a> [ ...]'",
		default="0.0,1.0,0.0,0.0,1.0 0.5,0.0,1.0,0.0,1.0 1.0,0.0,0.0,1.0,1.0", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'colors'})
	op.add_option("-t", "--ttl", dest="ttl",
		help="set the lifetime of packet points (in seconds)", default=None, type="float",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'ttl'})
	op.add_option("--xcolor", dest="xcolor", help="set the x-axis color",
		metavar="r,g,b,a", default="0.5,0.0,0.0,0.5",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'xcolor'})
	op.add_option("--ycolor", dest="ycolor", help="set the y-axis color",
		metavar="r,g,b,a", default="0.0,0.5,0.0,0.5",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'ycolor'})
	op.add_option("--zcolor", dest="zcolor", help="set the z-axis color",
		metavar="r,g,b,a", default="0.0,0.0,0.5,0.5",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'zcolor'})
	op.add_option("-s", "--spin", dest="spin",
		help="set the spin rate in degrees / second", default=10.0, type="float",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'spin'})
	op.add_option("--xmin", dest="xmin", help="x axis minimum address", metavar="a.b.c.d", default="0.0.0.0",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics', 'option': 'xmin'})
	op.add_option("--xmax", dest="xmax", help="x axis maximum address",
		metavar="a.b.c.d", default="255.255.255.255",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'xmax'})
	op.add_option("--ymin", dest="ymin", help="y axis minimum port",
		metavar="x", default=0, type="int", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'ymin'})
	op.add_option("--ymax", dest="ymax", help="y axis maximum port",
		metavar="x", default=65535, type="int", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'ymax'})
	op.add_option("--zmin", dest="zmin", help="z axis minimum address",
		metavar="a.b.c.d", default="0.0.0.0", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'zmin'})
	op.add_option("--zmax", dest="zmax", help="z axis maximum address",
		metavar="a.b.c.d", default="255.255.255.255",
		action='callback', callback=self.setconfigoption_cb,
		callback_kwargs={'config' : self.parser, 'section': 'graphics',
		'option': 'zmax'})
	op.add_option("--xcidrip", dest="xcidrip",
		help="x axis network range in CIDR (IP)", metavar="a.b.c.d", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'xcidrip'})
	op.add_option("--xcidrmask", dest="xcidrmask",
		help="x axis network range in CIDR (mask)", metavar="x", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'xcidrmask'})
	op.add_option("--zcidrip", dest="zcidrip",
		help="z axis network range in CIDR (IP)", metavar="a.b.c.d", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'zcidrip'})
	op.add_option("--zcidrmask", dest="zcidrmask",
		help="z axis network range in CIDR (mask)", metavar="z", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'zcidrmask'})
	op.add_option("--xbounds", dest="xbounds",
		help="x axis bounds type (range, cidr, device)", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'xbounds'})
	op.add_option("--zbounds", dest="xbounds",
		help="z axis bounds type (range, cidr, device)", action='callback',
		callback=self.setconfigoption_cb, callback_kwargs={'config' : self.parser,
		'section': 'graphics', 'option': 'zbounds'})

	options, args = op.parse_args(argv[1:])


    def listinterfaces(self, *args):
	network.listinterfaces()

    def setconfigoption_cb(self, longopt, shortopt, cmdvalue, parser, config=None,
		    section=None, option=None, value=None):
	if value is not None:
	    cmdvalue = value
	if config is not None and section is not None and option is not None and cmdvalue is not None:
	    self.parser.set(section, option, str(cmdvalue))

	else:
	    print "Not enough info for option: config=%s, section=%s, option=%s, cmdvalue=%s, value=%s" % (config, section, option, cmdvalue, value)


    def stop(self):
	"""Clean up this controller.  The ConfigurationController writes out the
	user's configuration at this time."""
	f = open(self.userfile, 'w')
	self.parser.write(f)
	f.close()

    def get(self, section, option):
	return self.parser.get(section, option)

    def set(self, section, option, value):
	return self.parser.set(section, option, value)

    def trace(self, section, option, callback):
	return self.parser.trace(section, option, callback)




class PygameEventsController(Controller):
    def __init__(self, config, section="events"):
	self.config = config
	self.section = section
	self.proproot = None

    def updateframesize(self, event):
	height = self.config.getint('display', 'height')
	width = self.config.getint('display', 'width')
	fullscreen = self.config.getboolean('display', 'fullscreen')
	linewidth = self.config.getint('display', 'linewidth')
	pointsize = self.config.getint('display', 'pointsize')
	display.resize(width, height, fullscreen, linewidth, pointsize)

    def propwidth_cb(self, section, option, value):
	self.proproot.win['width'] = value

    def propheight_cb(self, section, option, value):
	self.proproot.win['height'] = value

    def saveproprect(self):
	if self.proproot is not None:
	    dim, unk1, unk2 = self.proproot.geometry().split('+')
	    width, height = dim.split('x')

	    # geometry gets bigger each time - probably only windows.  don't know yet
	    # 20 might be the width of the scrollbar....
	    width = int(width) - 20
	    height = int(height) - 4

	    self.config.set('prefs', 'width', str(width))
	    self.config.set('prefs', 'height', str(height))
    
    def del_propsheet(self):
	if self.proproot is not None:
	    self.saveproprect()
	    Wm.withdraw(self.proproot)

    def process_event(self, event):
	control_mask = KMOD_SHIFT | KMOD_CTRL | KMOD_ALT | KMOD_META
	saverate = 0.0
	rate = 0.0

	if event is not None:
	    if event.type == pygame.VIDEORESIZE:
		#print "resize! event=%s" % event.h
		self.config.set('display', 'width', str(event.w))
		self.config.set('display', 'height', str(event.h))
		fullscreen = self.config.getboolean('display', 'fullscreen')
		self.updateframesize(None)
		#resize(event.w, event.h, fullscreen)

	    elif event.type == KEYDOWN:         
		if event.key == K_f:
		    fullscreen = self.config.getboolean('display', 'fullscreen')
		    if fullscreen:
			fullscreen = False
		    else:
			fullscreen = True
		    self.config.set('display', 'fullscreen', str(fullscreen))
		if event.key == K_s:
		    if saverate:
			rate = saverate
			saverate = None
		    else:
			saverate = rate
			rate = 0.0
		elif event.key == K_p:
		    display.screenshot("screen.png")
		elif event.key == K_c:
		    if self.proproot is None:
			import preferences
			self.proproot = Tk()
			self.proproot.withdraw()
			self.proproot.title('NetCube Preferences')

			propwidth = self.config.getint('prefs', 'width')
			propheight = self.config.getint('prefs', 'height')

			self.proproot.win = preferences.propsheet(master=self.proproot, config=self.config, width=propwidth, height=propheight)
			self.proproot.win.screen.resolution.width.bind("<FocusOut>", self.updateframesize)
			self.proproot.win.screen.resolution.height.bind("<FocusOut>", self.updateframesize)
			self.proproot.protocol('WM_DELETE_WINDOW', self.del_propsheet)
			self.proproot.win.pack(expand=1, fill=BOTH)
			self.proproot.deiconify()

			self.config.trace('prefs', 'width', self.propwidth_cb)
			self.config.trace('prefs', 'height', self.propheight_cb)
		    else:
			if self.proproot.state() == 'withdrawn':
			    self.proproot.deiconify()
			else:
			    self.proproot.withdraw()
			    self.saveproprect()
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
		
	    if event.type == QUIT or (event.type == KEYDOWN and
		    (event.key == K_ESCAPE or
			(event.key == K_F4 and event.mod & KMOD_ALT))):
		if self.proproot is not None:
		    self.saveproprect()
		raise QuitEvent()

    def run(self):
	ret = True
        # Let Tkinter do its thing:
	if self.proproot is not None:
	    self.proproot.update()

	# Process all pending pygame requests.  Using poll() only allows a
	# single event to be processed at a time. 
	#event = pygame.event.poll()
	events = pygame.event.get()
	for event in events:
	    #print "Processing event: %s" % event
	    status = self.process_event(event)

class SchedulerTarget:
    def __init__(self, func=None, mindelay=0):
	self.func = func
	self.mindelay = mindelay
	self.next = 0

class SchedulingController(Controller):
    def __init__(self, config, section='scheduler', perfevery=0):
	# TODO: Read timings from config?
	self.targets = {}
	self.next = 0
	self.perfevery = perfevery
	self.perfnext = 0
	self.perfvals = {'sleep': 0}

    def run(self):
	ticks = pygame.time.get_ticks()
	sleeptime = self.next - ticks
	if sleeptime < 0:
	    sleeptime = 0
	pygame.time.wait(sleeptime)
	self.perfvals['sleep'] += sleeptime

	if self.perfevery > 0 and self.perfnext < pygame.time.get_ticks():
	    out = ""
	    total = sum(self.perfvals.itervalues())
	    for name, val in self.perfvals.iteritems():
		if total > 0:
		    percentage = 100 * val / total
		else:
		    percentage = 0
		out += "%s=%d (%s)\t" % (name, val, percentage)
		self.perfvals[name] = 0
	    print out
	    self.perfnext = pygame.time.get_ticks() + self.perfevery

	    
	for name, target in self.targets.iteritems():
	    ticks = pygame.time.get_ticks()
	    if target.next < ticks:
		#print "  Running %s" % name
		target.func()
		target.next = pygame.time.get_ticks() + target.mindelay
		self.perfvals[name] += pygame.time.get_ticks() - ticks
	self.next = min([t.next for t in self.targets.itervalues()] + [self.perfnext])

    def add_target(self, name, func, mindelay=0):
	self.targets[name] = SchedulerTarget(func, mindelay)
	self.perfvals[name] = 0
