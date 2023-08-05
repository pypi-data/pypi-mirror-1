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


from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import pygame
from pygame.locals import *

def screenshot(width, height, filename=None):
    """Take a screen shot and save it to the given filename."""
    try:
	import Image
    except:
	print "Screenshot capability requires the Python Image Library (PIL)."
	return

    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    img = Image.fromstring("RGB", (width, height), data)
    if filename:
	img.save(filename)
    else:
	# TODO: save based on timestamp
	pass


def init():
    """Initialize the graphics framework.  This starts up pygame and creates the
    main window."""
    pygame.init()

    pygame.key.set_repeat(500, 30)
    
    pygame.display.set_caption("Cube Graphics")

def initviewport(left, top, width, height, linewidth, pointsize):
    """Initialize the OpenGL context with the given settings."""

    # Clear out the OpenGL matrices
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Initialize the OpenGL viewport and frustrum
    glViewport(left, top, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width-left)/float(height-top), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    # Set the basic screen settings and features
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_LINE_SMOOTH)
    #glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    # Set up the base linewidth and pointsize
    glLineWidth(float(linewidth))
    glPointSize(pointsize)




def resize(width, height, fullscreen, linewidth, pointsize):
    """Resize the viewport to the given size and configure the new viewport with the given width, height, linewidth, and pointsize and use fullscreen mode according to the fullscreen parameter."""
    #print "resizing to:  width=%s, height=%s, fullscreen=%s, type=%s" % (width, height, fullscreen, type(fullscreen))



    # First figure out whether fullscreen is being toggled.  If so, then the
    # state must be saved, the display must be reset, and the state must be
    # restored.


    # Check for an existing display.
    res = pygame.display.get_surface()
    if res is not None:

	# We already have a display, so we'll have to break it down first - save off the current state.
	mode = res.get_flags()

	# Check whether we have to toggle fullscreen.
	if bool(mode & pygame.FULLSCREEN) ^ fullscreen:
	    # have to reset the display
	    #print "Resetting display"
	    caption = pygame.display.get_caption()

	    # if fullscreen now, then do graceful "shutdown"...
	    if mode & pygame.FULLSCREEN:
		#print "Disabling opengl before switch"
		pygame.display.set_mode((width, height), mode ^ pygame.OPENGL)

	    # Restart the pygame display
	    pygame.display.quit()
	    pygame.display.init()

	    # if fullscreen now, then do graceful "shutdown"...
	    if mode & pygame.FULLSCREEN:
		#print "Disabling opengl before switch"
		pygame.display.set_mode((width, height), (mode ^ pygame.OPENGL) ^ pygame.FULLSCREEN)

	    pygame.display.set_caption(*caption)
    else:
	# set up initial state
	mode = OPENGL | DOUBLEBUF
    #print "mode=%s, mode & FULLSCREEN=%s" % (long(mode), bool(mode & pygame.FULLSCREEN))



    # Add the FULLSCREEN flag to the mode if necessary otherwise make sure it is removed.
    #

    if fullscreen:
	#print "Enabling fullscreen"
	mode = mode | pygame.FULLSCREEN
	if mode & pygame.RESIZABLE:
	    mode = mode ^ pygame.RESIZABLE
    else:
	#print "Disabling fullscreen"
	if mode & pygame.FULLSCREEN:
	    mode = mode ^ pygame.FULLSCREEN
	mode = mode | pygame.RESIZABLE

    #print "mode=%s, mode & FULLSCREEN=%s" % (mode, bool(mode & pygame.FULLSCREEN))

    res = pygame.display.set_mode((width, height), mode)
    #print "set_mode result: %s, %s" % (res, res.get_rect())
    left, top, twidth, theight = res.get_rect()

    pygame.key.set_mods(0)


    # Initialize the new viewport
    initviewport(left, top, twidth, theight, linewidth, pointsize)


    # Turn off the mouse cursor if we are in fullscreen mode
    if fullscreen:
	pygame.mouse.set_visible(0)
    else:
	pygame.mouse.set_visible(1)


def updatelinewidth(linewidth):
    """Sets the opengl line width."""
    glLineWidth(float(linewidth))

def updatepointsize(pointsize):
    """Sets the opengl point size."""
    glPointSize(float(pointsize))

def toggle_fullscreen():
    """Toggles fullscreen mode, saving state and rebuilding the context as
    necessary.  Returns the screen resolution as a tuple."""
    if pygame.display.get_init():
	screen = pygame.display.get_surface()
	caption = pygame.display.get_caption()
	
	w,h = screen.get_width(),screen.get_height()
	flags = screen.get_flags()
	bits = screen.get_bitsize()
	
	pygame.display.quit()
    pygame.display.init()
    
    screen = pygame.display.set_mode((w,h),flags^FULLSCREEN,bits)
    pygame.display.set_caption(*caption)
 
    pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??
    
    return screen

    

def clear():
    """Clears the display.  This can be used before rendering each frame."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def flip():
    """Flips the display when in double-buffer mode.  This can be used after
    rendering a frame in order to show it on the screen."""
    pygame.display.flip()
