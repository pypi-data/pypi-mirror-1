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

def init(width, height, pointsize=1.0, linewidth=1.0, fullscreen=False):
    global screenwidth, screenheight
   
    screenwidth = width
    screenheight = height

    pygame.init()

    pygame.key.set_repeat(500, 30)
    
    mode = OPENGL | DOUBLEBUF
    if fullscreen:
	mode = mode | FULLSCREEN
	pygame.mouse.set_visible(0)
    pygame.display.set_mode((width, height), mode)
    pygame.display.set_caption("Cube Graphics")
    
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LINE_SMOOTH)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLineWidth(linewidth)
    glPointSize(pointsize)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
   
#def add_packet_point(pktlen, data, timestamp):
def add_packet_point(header, data):
    global startttl, dumper
    global xmin, xmax, ymin, ymax, zmin, zmax
   
    time_s, time_ms = header.getts()
    caplen = header.getcaplen() 

    if not data:
	return

    if dumper:
	dumper.dump(header, data)   
 
    if data[12:14]=='\x08\x00':
	packet = data[14:]
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
    
    if argv is None:
	argv = sys.argv
    
    
    parser = OptionParser("usage: %prog [options] [interface filter]")
    parser.add_option("-i", "--interface", dest="interface", help="read packets from INTERFACE", metavar="INTERFACE")
    parser.add_option('-l', '--list', action='callback', callback=listinterfaces)
    parser.add_option("-f", "--fullscreen", dest="fullscreen", help="display in fullscreen mode", default=False, action="store_true")
    #parser.add_option("-f", "--filterfile", dest="filterfile", help="read packet filter from FILE", metavar="FILE")
    parser.add_option("-p", "--promisc", dest="promisc", help="put the interface into promiscuous mode", default=False, action="store_true")
    parser.add_option("-P", "--nopromisc", dest="promisc", help="DO NOT put the interface into promiscuous mode", default=False, action="store_false")
    parser.add_option("-r", "--read", dest="readfile", help="read packets previously captured to FILE", metavar="FILE")
    parser.add_option("-w", "--write", dest="writefile", help="write packets to FILE", metavar="FILE")
    parser.add_option("--pointsize", dest="pointsize", help="set the point size to SIZE pixels", metavar="SIZE", default=1.0, type="float")
    parser.add_option("--linewidth", dest="linewidth", help="set the line width to WIDTH pixels", metavar="WIDTH", default=1.0, type="float")
    parser.add_option("--fps", dest="fps", help="attempt to display FRAMES frames per second", metavar="FRAMES", default=30, type="int")
    parser.add_option("--width", dest="width", help="set display width to WIDTH pixels", metavar="WIDTH", default=320, type="int")
    parser.add_option("--height", dest="height", help="set display height to HEIGHT pixels", metavar="HEIGHT", default=240, type="int")
    parser.add_option("-c", "--colors", dest="colors", help="set the vertical gradient colors", metavar="'<y,r,g,b,a> [ ...]'", default="0.0,1.0,0.0,0.0,1.0 0.5,0.0,1.0,0.0,1.0 1.0,0.0,0.0,1.0,1.0")
    parser.add_option("-t", "--ttl", dest="ttl", help="set the lifetime of packet points (in seconds)", default=None, type="float")
    #parser.add_option("--xcolor", dest="xcolor", help="set the x-axis color", metavar="r,g,b,a", default="0.0,0.3,0.1,0.5")
    #parser.add_option("--ycolor", dest="ycolor", help="set the y-axis color", metavar="r,g,b,a", default="0.0,0.3,0.1,0.5")
    #parser.add_option("--zcolor", dest="zcolor", help="set the z-axis color", metavar="r,g,b,a", default="0.0,0.3,0.1,0.5")
    parser.add_option("--xcolor", dest="xcolor", help="set the x-axis color", metavar="r,g,b,a", default="0.5,0.0,0.0,0.5")
    parser.add_option("--ycolor", dest="ycolor", help="set the y-axis color", metavar="r,g,b,a", default="0.0,0.5,0.0,0.5")
    parser.add_option("--zcolor", dest="zcolor", help="set the z-axis color", metavar="r,g,b,a", default="0.0,0.0,0.5,0.5")
    parser.add_option("-s", "--spin", dest="spin", help="set the spin rate in degrees / second", default=10.0, type="float")
    parser.add_option("--xmin", dest="xmin", help="x axis minimum address", metavar="a.b.c.d", default="0.0.0.0")
    parser.add_option("--xmax", dest="xmax", help="x axis maximum address", metavar="a.b.c.d", default="255.255.255.255")
    parser.add_option("--ymin", dest="ymin", help="y axis minimum port", metavar="x", default=0, type="int")
    parser.add_option("--ymax", dest="ymax", help="y axis maximum port", metavar="x", default=65535, type="int")
    parser.add_option("--zmin", dest="zmin", help="z axis minimum address", metavar="a.b.c.d", default="0.0.0.0")
    parser.add_option("--zmax", dest="zmax", help="z axis maximum address", metavar="a.b.c.d", default="255.255.255.255")
    parser.add_option("--xrange", dest="xrange", help="x axis network range in CIDR", metavar="a.b.c.d/x")
    parser.add_option("--zrange", dest="zrange", help="z axis network range in CIDR", metavar="a.b.c.d/x")
    parser.add_option("--xusedevrange", dest="xusedevrange", help="get x axis range from network device", default=False, action="store_true")
    parser.add_option("--zusedevrange", dest="zusedevrange", help="get z axis range from network device", default=False, action="store_true")


    options, args = parser.parse_args(argv[1:])
    interfaces = pcapy.findalldevs()
    if options.interface:
	interface = options.interface

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
    
    #filterfile = options.filterfile
    promisc = options.promisc
    readfile = options.readfile
    writefile = options.writefile
    pointsize = options.pointsize
    linewidth = options.linewidth
    fullscreen = options.fullscreen
    desiredframes = options.fps
    width = options.width
    height = options.height
    colorlist = options.colors
    startttl = options.ttl
    if startttl < 0:
	startttl = None
    rate = options.spin
    xcolor = options.xcolor
    ycolor = options.ycolor
    zcolor = options.zcolor
    if len(args) > 0:
	filter = string.join(args)
    else:
	filter = "tcp[tcpflags] == tcp-syn"
    
    xmin = struct.unpack('I', socket.inet_aton(options.xmin))[0]
    if options.xmax is "255.255.255.255":
	xmax = 2**32-1
    else:
	xmax = struct.unpack('I', socket.inet_aton(options.xmax))[0]

    ymin = options.ymin
    ymax = options.ymax
    zmin = struct.unpack('I', socket.inet_aton(options.zmin))[0]
    if options.zmax is "255.255.255.255":
	zmax = 2**32-1
    else:
	zmax = struct.unpack('I', socket.inet_aton(options.zmax))[0]

    xrange = options.xrange
    zrange = options.zrange    
    if xrange:
	xmin, xmax = iprange(xrange)

    if zrange:
	zmin, zmax = iprange(zrange) 

    # Note that xmax and zmax checks are delayed for xusedevrange and zusedevrange

    xusedevrange = options.xusedevrange
    zusedevrange = options.zusedevrange



    r, g, b, a = string.split(xcolor, ",")
    xcolor = (float(r), float(g), float(b), float(a))

    r, g, b, a = string.split(ycolor, ",")
    ycolor = (float(r), float(g), float(b), float(a))
    
    r, g, b, a = string.split(zcolor, ",")
    zcolor = (float(r), float(g), float(b), float(a))
    
    for entry in string.split(colorlist):
	y, r, g, b, a = string.split(entry, ",")
	colors[float(y)] = (float(r), float(g), float(b), float(a))
 




    # Initialize networking
    p = None
    if readfile:
	p = pcapy.open_offline(readfile)
    else:
	p = pcapy.open_live(interface, 68, promisc, 100)
	
    net = p.getnet()
    mask = p.getmask()

    if xusedevrange:
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

    if zusedevrange:
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


    
    if filter:
	p.setfilter(filter)
    
    if writefile:
	dumper = p.dump_open(writefile)

    p.setnonblock(1)


    # Initialize graphics
    init(width, height, pointsize, linewidth, fullscreen)
    resize(width, height)

    rotation = 0.0
    frames = 0
    clock = pygame.time.Clock()

    ticks = startticks = pygame.time.get_ticks()
    saverate = None    

    control_mask = KMOD_SHIFT | KMOD_CTRL | KMOD_ALT | KMOD_META

    while 1:
	event = pygame.event.poll()
	if event.type == KEYDOWN:         
            if event.key == K_s:
                if saverate:
                    rate = saverate
                    saverate = None
                else:
                    saverate = rate
                    rate = 0.0
	    elif event.key == K_p:
		screenshot("screen.png")
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
                                
            
	if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
	    break;

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

	clock.tick(desiredframes)

    #print "fps:  %d" % ((frames * 1000) / (pygame.time.get_ticks() - startticks))


if __name__ == "__main__":
    sys.exit(main())
    
