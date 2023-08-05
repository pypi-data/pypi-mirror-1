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
import traceback

import pygame
from pygame.locals import *
import pygame.mouse
import pcapy
import socket
import struct
import string
from optparse import OptionParser
import re

from Tkinter import *

from config import TkinterConfigParser
import network
import display

 
def main(argv=None):
    from controllers import ConfigurationController, NetworkController, DisplayController, GraphicsController, PygameEventsController, SchedulingController, QuitEvent


    # Create application controllers
    configcon = ConfigurationController(argv=argv)
    networkcon = NetworkController(config=configcon.parser)
    displaycon = DisplayController(config=configcon.parser)
    graphicscon = GraphicsController(config=configcon.parser)
    networkcon.grapher = graphicscon.grapher
    eventcon = PygameEventsController(config=configcon.parser)


    # Schedule the controllers.  Profiling is disabled using perfevery=0
    schedcon = SchedulingController(config=configcon.parser, perfevery=0)
    schedcon.add_target('network', networkcon.run, mindelay=100)
    schedcon.add_target('display', displaycon.run, mindelay=100)
    schedcon.add_target('graphics', graphicscon.run, mindelay=100)
    schedcon.add_target('events', eventcon.run, mindelay=100)


    # FPS is controlled by telling the scheduler run the GraphicsController only so often.
    def update_fps(s=None, o=None, v=None):
	v = configcon.parser.getfloat('display', 'fps')
	if v > 0:
	    schedcon.targets['graphics'].mindelay = int(1000.0 / configcon.parser.getfloat('display', 'fps'))
	else:
	    schedcon.targets['graphics'].mindelay = 0

    configcon.parser.trace('display', 'fps', update_fps)
    update_fps()


    # Make sure we don't loose our arguments for some reason
    if argv is None:
	argv = sys.argv


    # Ensure that the capture filter gets updated on config changes
    def updatefilter(s, o, v):
	try:
	    networkcon.reader.reader.setfilter(v)
	except pcapy.PcapError, e:
	    print "Invalid filter: %s" % v

    configcon.parser.trace('capture', 'filter', updatefilter)


    ###################
    ###  The Guts of the loop, surprisingly enough
    ###################
    while 1:

	# Run the scheduler, waiting for a QuitEvent
	try:
	    schedcon.run()
	except QuitEvent:
	    break


    # Save the current configuration on exit
    configcon.stop()


if __name__ == "__main__":
    import time

    # The main function attempts to recover from exceptions by restarting the
    # cube.  This delay is used to wait after an exception occurs in order to
    # give the user some time to act.  If the delay is set to 0 then it
    # disables the loop.  This would ideally be configurable (just like
    # everything else!).
    delay = 5
    run_times = 1

    while delay > 0 or run_times > 0:
	if run_times > 0:
	    run_times -= 1

	# Run main.  If it exits normally, great.  If not, then check if it was
	# the user hitting Ctrl-C (KeyboardInterrupt) or them closing the
	# window (SystemExit) and treat it as normal.  Otherwise, print the
	# exception, sleep for <delay> seconds and start it up again. 
	try:
	    sys.exit(main())
	except SystemExit:
	    break
	except KeyboardInterrupt:
	    break
	except Exception, e:
	    print "Exception: %s" % e
	    traceback.print_exc(file=sys.stdout)
	
	    print "Sleeping %s seconds before restart..." % delay
	    time.sleep(delay)

	    continue
