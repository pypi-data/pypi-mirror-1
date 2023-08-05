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

from scenegraph import *

class NetworkCube(ColorCube):
    """A subclass of ColorCube that uses the inside space of the cube to
    display a scatter plot of points according to network data.  The axes
    correspond to the source address, destination address, and destination port
    of network packets."""
    def __init__(self):
	"""Initialize a new NetworkCube.  This sets up axis minimums and
	maximums to their most extreme values and associates the x, y, and z
	axes with the packet source address, destination port, and destination
	address, respectively.  Additionally the color of each point
	corresponds to the destination port of the packet to ease visual
	interpretation of the interface."""
	ColorCube.__init__(self)
    
	self.optimize = 0

	self.data = []
	self.optdata = None
	self.optdatalen = 0
	self.unop_loops = 0

	self.xmin = 0
	self.xmax = 2**32-1
	self.ymin = 0
	self.ymax = 2**16-1
	self.zmin = 0
	self.zmax = 2**32-1

	self.colors = {}

	self.map = {'x': 'ip_packet.source_address_n',
		    'y': 'ip_packet.tcp_packet.destination_port',
		    'z': 'ip_packet.destination_address_n',
		    'color': 'ip_packet.tcp_packet.destination_port'}

    def value_for_axis(self, data, axis):
	"""Pull a value from the given data according to the NetworkCube's
	mapping for the given axis.  For instance, by default the y axis is
	associated with a data packets ip_packet.tcp_packet.destination_port
	value.  This function retrieves that destination_port value from the
	data when axis is set to 'y'."""
	stack = []
	path = self.map[axis].split('.')
	d = data
	for pel in path:
	    if d is not None and d.has_key(pel):
		d = d[pel]
		stack.append(d)
	    else:
		return None

	#print 'stack=', stack
	return d

    def color_for_val(self, y):
	"""Return a color tuple (r,g,b,a) calculated from the list of colors
	given to the cube based on the y value given here where y >= 0.0 and y
	<= 1.0.  So, on a small scale, if the color list was the following:

	    self.colors = {
		'0.0': (1.0, 0.0, 0.0, 0.5),
		'0.5': (0.0, 1.0, 0.0, 0.5),
		'1.0': (0.0, 0.0, 1.0, 0.5)
	    }
	    
	Then calling this function with a domain of values from 0.0 to 1.0
	would produce a range of results corresponding to a gradient from red
	at 0.0 to green at 0.5 to blue at 1.0 all the while maintaining a 50%
	transparency."""

	# find y in color list range
	# calculate and return corresponding color

	# Run through all of the colors in the list, narrowing it down to the
	# two colors that are above and below the index, y.
	lower, upper = 0.0, 1.0
	for k, v in self.colors.items():
	    if lower < k and k < y:
		lower = k
	    elif y < k and k < upper:
		upper = k

	# Get the color values for the two "book-ends"
	lowcolor = self.colors[lower]
	highcolor = self.colors[upper]

	# Find the desired color on a linear scale between the two book-ends.
	mod = (y - lower) / (upper - lower)
	r = lowcolor[0] + mod * (highcolor[0] - lowcolor[0])
	g = lowcolor[1] + mod * (highcolor[1] - lowcolor[1])
	b = lowcolor[2] + mod * (highcolor[2] - lowcolor[2])
	a = lowcolor[3] + mod * (highcolor[3] - lowcolor[3])

	return (r, g, b, a)


    def draw_points(self, points):
	"""Execute OpenGL commands to draw the points in this object's data
	set.  For each point set the color using the
	NetworkCube.color_for_val(y) method."""
	for datum in points:
	    d = {}
	    for a in self.map.keys():
		d[a] = self.value_for_axis(datum, a)
	    in_range = lambda v, min, max: min <= v and v <= max

	    #print "d=%s" % (d,)
	    x, y, z, color = [d[key] for key in ('x', 'y', 'z', 'color')]
	    if in_range(x, self.xmin, self.xmax) and in_range(y, self.ymin, self.ymax) and in_range(z, self.zmin, self.zmax):

		# Scale the raw values to be between 0.0 and 1.0 corresponding
		# to the min and max values for each axis.
		x = (x - self.xmin) / float(self.xmax-self.xmin)
		y = (y - self.ymin) / float(self.ymax-self.ymin)
		z = (z - self.zmin) / float(self.zmax-self.zmin)
		color = (color - self.ymin) / float(self.ymax-self.ymin)
		glColor4f(*self.color_for_val(color))
		glVertex3f(x, y, z)

    def render(self):
	"""Render this object's pieces.  Note that the points are optionally
	organized into display lists based on a basic optimization schedule.
	Whenever 500 points have been added or after 30000 loops of having any
	un-optimized points it will re-create a display list.  During rendering
	this display list is rendered and then any unoptimized points are
	rendered."""
	# Do any prerendering - translations, etc.
	GLObject._prerender(self)

	# Draw the axis lines (cube shape)
	glBegin(GL_LINES)
	ColorCube._render(self)
	glEnd()

	l = len(self.data)
	
	# If optimization is enabled, then optimize every 500 points or every
	# 30000 loops if there are any unoptimized points.  This method of
	# optimization uses a display list.  It may be possible to get better
	# gains from vertex arrays or by using display lists in a different
	# fashion.  For instance, multiple display lists or possibly adding
	# points to the existing list rather than recreating it entirely.
	if self.optimize == 1 and (l - self.optdatalen > 500 or (self.unop_loops > 30000 and l > self.optdatalen)):
	    print "Rebuilding list optdata=%s, optdatalen=%s, l=%s" % (self.optdata, self.optdatalen, l)
	    if self.optdata is not None:
		glDeleteLists(self.optdata, 1)

	    # We just need one display list (for now!)
	    self.optdata = glGenLists(1)
	    self.optdatalen = l
	    glNewList(self.optdata, GL_COMPILE_AND_EXECUTE)

	    # Add all of the points to the display list
	    glBegin(GL_POINTS)
	    self.draw_points(self.data)
	    glEnd()

	    glEndList()

	    # Reset the counter for the next re-optimization
	    self.unop_loops = 0

	else:
	    # If we have a display list, execute it
	    if self.optdata is not None:
		glCallList(self.optdata)

	    # Display all unoptimized points (could be everything)
	    glBegin(GL_POINTS)
	    self.draw_points(self.data[self.optdatalen:len(self.data)])
	    glEnd()

	    # Increment the re-optimization counter if necessary
	    if l > self.optdatalen:
		self.unop_loops += 1

	# Take care of post-rendering
	GLObject._postrender(self)



