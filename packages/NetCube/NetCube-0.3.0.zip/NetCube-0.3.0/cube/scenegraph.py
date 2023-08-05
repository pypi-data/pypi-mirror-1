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

"""Scene graph classes to simplify OpenGL rendering.

Scenegraph aims to reduce the complexity in rendering 3-dimensional objects
using OpenGL.  It provides a system of frames of reference and a set of
primitive objects that can be used to build up complex scense.  All of these
objects can be modified and updated during the lifetime of the objects in order
to update the scene.  Any GLFrame can contain another GLObject and the child
object's position and rotation are relative to that of the parent object.
"""

from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import network

class GLTransform(object):
    """A stub class to define a transformation that can be applied to a
    GLObject.

    Subclasses should implement the apply() method.
    """
    def apply(self):
	"""Apply this transformation in the current OpenGL context.  This
	method is called before a GLObject is rendered."""
	pass

class Rotation(GLTransform):
    """A GLTransform that rotates the current OpenGL context."""
    def __init__(self, r, x, y, z):
	"""Initialize a new Rotation GLTransform with a rotation of r about the
	vector defined by x, y, and z."""
	self.r = r
	self.x = x
	self.y = y
	self.z = z

    def apply(self):
	"""Apply this transformation in the current OpenGL context.  This
	method is called before a GLObject is rendered.  Calls glRotate with
	the rotation parameters stored in this object."""
	glRotate(self.r, self.x, self.y, self.z)


class InverseRotation(Rotation):
    """A GLTransform that takes a Rotation object, calculates the opposite
    "spin," and then rotate's the GL context accordingly.  Currently this is
    used to produce billboards."""
    def __init__(self, source):
	self.source = source

    def apply(self):
	glRotate(-self.source.r, self.source.x, self.source.y, self.source.z)

class Translation(GLTransform):
    """A GLTransform that translates the current OpenGL context in space."""
    def __init__(self, x, y, z):
	"""Initialize a new Translation GLTransform with a translation in each
	of the x, y, and z axes by an amount specified in the x, y, and z
	arguments."""
	self.x = x
	self.y = y
	self.z = z

    def apply(self):
	"""Apply this transformation in the current OpenGL context.  This
	method is called before a GLObject is rendered.  Calls glTranslatef
	with the translation parameters stored in this object."""
	glTranslatef(self.x, self.y, self.z)

class Scale(GLTransform):
    """A GLTransform that scales the current OpenGL context in space."""
    def __init__(self, x, y, z):
	"""Initialize a new Scale GLTransform with a scale in each
	of the x, y, and z axes by an amount specified in the x, y, and z
	arguments."""
	self.x = x
	self.y = y
	self.z = z

    def apply(self):
	"""Apply this transformation in the current OpenGL context.  This
	method is called before a GLObject is rendered.  Calls glScalef with
	the scale parameters stored in this object."""
	glScalef(self.x, self.y, self.z)

class Color(GLTransform):
    """A GLTransform that sets the color in the current OpenGL context."""
    def __init__(self, r, g, b, a=1.0):
	"""Initialize a new Color GLTransform with an RGBA color given by the
	r, g, b, and a arguments."""
	self.r = r
	self.g = g
	self.b = b
	self.a = a

    def apply(self):
	"""Apply this transformation in the current OpenGL context.  This
	method is called before a GLObject is rendered.  Calls glColor4f with
	the color parameters stored in this object."""
	glColor4f(self.r, self.g, self.b, self.a)

class Identity(GLTransform):
    """A GLTransform that loads the identity matrix into the current OpenGL
    context."""
    def apply(self):
	"""Apply this transformation in the current OpenGL context.  This
	method is called before a GLObject is rendered.  Calls glLoadIdentity with
	the color parameters stored in this object."""
	glLoadIdentity()

class GLObject(object):
    """An object in an OpenGL scene.  This object can have GLTransforms added
    to it that get applied, in order of addition, to the OpenGL context before
    the object is rendered. 
    """
    def __init__(self):
	"""Initialize a new GLObject with an empty set of transforms."""
	self.transforms = []

    def pushTransform(self, trans):
	"""Push a new transform onto this GLObject."""
	self.transforms.append(trans)

    def pushRotation(self, r, x, y, z):
	"""Convenience function to push a new Rotation GLTransform onto this
	object's list of transforms."""
	self.pushTransform(Rotation(r, x, y, z))

    def pushTranslation(self, x, y, z):
	"""Convenience function to push a new Translation GLTransform onto this
	object's list of transforms."""
	self.pushTransform(Translation(x, y, z))

    def pushScale(self, x, y, z):
	"""Convenience function to push a new Scale GLTransform onto this
	object's list of transforms."""
	self.pushTransform(Scale(x, y, z))

    def pushColor(self, r, g, b, a=1.0):
	"""Convenience function to push a new Color GLTransform onto this
	object's list of transforms."""
	self.pushTransform(Color(r, g, b, a))

    def popTransform(self):
	"""Removes the last transform off of this object's list of transforms
	and returns that transform."""
	return self.transforms.pop()

    def _prerender(self):
	"""This method pushes the current GL matrix and applies this object's
	transforms.  It is called just before this object is rendered."""
	glPushMatrix()
	for t in self.transforms:
	    t.apply()

    def _postrender(self):
	"""This method pops the current GL matrix.  It is called just after
	this object is rendered."""
	glPopMatrix()

    def render(self):
	"""Renders this object.  In the base implementation, this simply calls
	_prerender and _postrender and does not perform any OpenGL functions
	directly."""
	self._prerender()
	self._postrender()

class GLFrame(GLObject):
    """Defines a GLObject that contains other GLObjects.  These objects are
    then rendered and transformed relative to this frame's transforms.

    This is useful to define a reference frame that can be moved or otherwise
    transformed without having to specify those transforms on each object in
    the frame.  Children are added by modifying the children property of the
    GLFrame.
    """
    def __init__(self):
	"""Initialize a new GLFrame with an empty list of children."""
	self.children = []
	GLObject.__init__(self)

    def render(self):
	"""Applies this frame's transforms and then renders each child
	GLObject."""
	self._prerender()
	for child in self.children:
	    child.render()
	self._postrender()

class BlackoutFrame(GLFrame):
    """Defines a GLFrame that conditionally displays its child objects based on
    a function given to the object."""
    def __init__(self, test):
	"""Initialize a new BlackoutFrame using test as a function to check for
	whether the frame's children should be rendered."""
	GLFrame.__init__(self)
	self.test = test

    def render(self):
	"""Run the test function.  If it evaluates to True then render this
	frame and its children."""
	if self.test():
	    GLFrame.render(self)

class LineWidthFrame(GLFrame):
    """Defines a GLFrame that changes the OpenGL linewidth within the frame and
    resets it to another value afterwards.  Both of these values must be
    maintained as this class does not query OpenGL for the current
    linewidth."""
    def __init__(self, fromwidth, towidth):
	"""Initialize a new LineWidthFrame.  fromwidth corresponds to the
	parent frame's linewidth.  towidth corresponds to the linewidth used
	within this frame."""
	GLFrame.__init__(self)
	self.fromwidth = fromwidth
	self.towidth = towidth

    def render(self):
	"""Applies glLineWidth(towidth), applies this frame's transforms and
	then renders each child GLObject, and applies
	glLineWidth(fromwidth)."""
	glLineWidth(self.towidth)
	GLFrame.render(self)
	glLineWidth(self.fromwidth)

class GLCube(GLObject):
    """Defines a unit cube that can be rendered via OpenGL."""
    def _prerender(self):
	GLObject._prerender(self)
	glBegin(GL_LINES)

    def _postrender(self):
	glEnd()
	GLObject._postrender(self)

    def _renderonaxis(self, x):
	"""Render the edges that are paralell to x.  x should be one of i, j,
	or k, the unit vectors along the x, y, and z axes.
	"""
	import vector
	working_a = x
	working_b, working_c = filter(lambda g: g != working_a, vector.unit_vectors)
	for u in (vector.origin, working_b, working_c, working_b + working_c):
	    self._drawline(u, u + working_a)

    def _drawline(self, origin, vector):
	"""Called after this object's _prerender method, this method draws a
	line from origin to vector."""
	glVertex3f(*origin)
	glVertex3f(*vector)

    def renderX(self):
	"""Renders the edges parallel to the x axis."""
	import vector
	self._renderonaxis(vector.i)

    def renderY(self):
	"""Renders the edges parallel to the y axis."""
	import vector
	self._renderonaxis(vector.j)

    def renderZ(self):
	"""Renders the edges parallel to the z axis."""
	import vector
	self._renderonaxis(vector.k)

    def render(self):
	"""Renders this cube."""
	self._prerender()

	self.renderX()
	self.renderY()
	self.renderZ()

	self._postrender()

class ColorCube(GLCube):
    """Extends GLCube to optionally set the color of the edges parallel to each
    axis in a different color.  For example, the edges parallel to the x axis
    can have one color while those parallel to the y axis have another and
    those parallel to the z axis have yet another color. 
    """
    def __init__(self, xcolor=(0.5, 0.5, 0.5, 0.5), ycolor=(0.5, 0.5, 0.5, 0.5), zcolor=(0.5, 0.5, 0.5, 0.5)):
	"""Initialize a new ColorCube.

	Colors are specified as 4-tuples.  They may be given in the xcolor,
	ycolor, and zcolor arguments or may later be set using the xcolor,
	ycolor, and zcolor properties.

	If no colors are set, the default for each set of edges is (0.5, 0.5, 0.5, 0.5).
	"""
	GLCube.__init__(self)
	self.xcolor = xcolor
	self.ycolor = ycolor
	self.zcolor = zcolor

    def render(self):
	"""Render the ColorCube using the colors previously set."""
	self._prerender()
	self._render()
	self._postrender()

    def _render(self):
	r, g, b, a = self.xcolor
	Color(r, g, b, a).apply()
	self.renderX()

	r, g, b, a = self.ycolor
	Color(r, g, b, a).apply()
	self.renderY()

	r, g, b, a = self.zcolor
	Color(r, g, b, a).apply()
	self.renderZ()

class ScatterPlot3d(GLObject):
    """A three dimensional scatter plot of data.  This is used to display data
    points within a cube."""
    def __init__(self):
	self.points = []
	self.xmin = 0
	self.xmax = 2**32-1
	self.ymin = 0
	self.ymax = 65535
	self.zmin = 0
	self.zmax = 2**32-1
	self.ttl = None

    #def add_packet_point(pktlen, data, timestamp):
    def add_packet_point(header, data):
	#global dumper
	#global xmin, xmax, ymin, ymax, zmin, zmax
	#global config
       
	time_s, time_ms = header.getts()
	caplen = header.getcaplen() 

	if not data:
	    return

	#if dumper:
	#    dumper.dump(header, data)   
     
	#if data[12:14]=='\x08\x00':
	frame = network.decode_ethernet_frame(data)
	if frame['type'] == 'Ethernet II':
	    if frame['ethernet_type'] == '\x08\x00':
		packet = data[14:]
	    elif frame['ethernet_type'] == '\x18\x00':
		packet = data[16:]
	    else:
		return

	    decoded = network.decode_ip_packet(packet)

	    # TCP
	    if decoded['protocol'] == socket.IPPROTO_TCP:
		decoded['tcp_packet'] = network.decode_tcp_packet(decoded['data'])
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
	    if self.xmax == self.xmin:
		#print "xmax == xmin"
		x = 0.5
	    else:
		#print "x = float(%d-%d)/float(%d-%d)" % (source, xmin, xmax, xmin)
		x = float(source-self.xmin)/float(self.xmax-self.xmin)

	    if self.ymax == self.ymin:
		#print "ymax == ymin"
		y = 0.5
	    else:
		#print "y = float(%d-%d)/float(%d-%d)" % (source, ymin, ymax, ymin)
		y = float(port-self.ymin)/float(self.ymax-self.ymin)

	    if self.zmax == self.zmin:
		#print "zmax == zmin"
		z = 0.5
	    else:
		#print "z = float(%d-%d)/float(%d-%d)" % (source, zmin, zmax, zmin)
		z = float(dest-self.zmin)/float(self.zmax-self.zmin)

     
	    if x < 0.0 or x > 1.0 or y < 0.0 or y > 1.0 or z < 0.0 or z > 1.0:
		return

	    lower, upper = 0.0, 1.0
	    for k, v in self.colors.items():
		if lower < k and k < y:
		    lower = k
		elif y < k and k < upper:
		    upper = k
	    lowcolor = self.colors[lower]
	    highcolor = self.colors[upper]
	    mod = (y - lower) / (upper - lower)
	    r = lowcolor[0] + mod * (highcolor[0] - lowcolor[0])
	    g = lowcolor[1] + mod * (highcolor[1] - lowcolor[1])
	    b = lowcolor[2] + mod * (highcolor[2] - lowcolor[2])
	    a = lowcolor[3] + mod * (highcolor[3] - lowcolor[3])

	    #startttl = config.getfloat('display', 'ttl')
	    startttl = self.ttl
	    if startttl < 0:
		startttl = None
	    points.append(((x, y, z), (r, g, b, a), startttl))

LEFT, CENTER, RIGHT = 1, 2, 3
GLUT_STROKE_ROMAN = GLUT_STROKE_ROMAN

class StrokeText(GLObject):
    def __init__(self, text=None, font=GLUT_STROKE_ROMAN, align=LEFT):
	GLObject.__init__(self)
	self.text = text
	self.font = font
	self.align = align

    def drawStrokeString(self, text, font):
	for c in text:
	    glutStrokeCharacter(font, ord(c))

    def stringLength(self, text, font):
	w = 0
	for c in text:
	    w += glutStrokeWidth(font, ord(c))

	return w

    def render(self):
	self._prerender()
	width = self.stringLength(self.text, self.font)
	if self.align == LEFT:
	    shift = 0.0
	elif self.align == CENTER:
	    shift = 0.0 - width/2.0
	elif self.align == RIGHT:
	    shift = 0.0 - double(width)

	glTranslate(shift, 0.0, 0.0)
	self.drawStrokeString(self.text, self.font)
	self._postrender()
