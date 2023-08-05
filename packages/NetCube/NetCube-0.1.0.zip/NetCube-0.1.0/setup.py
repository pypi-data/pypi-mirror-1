#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages
setup(
	name = 'NetCube',
	version = '0.1.0',
	packages = find_packages(),
	#scripts = ['cube/cube.py'],
	entry_points = {
	    'console_scripts' : [
		'cube = cube.cube:main',
		],
	    'gui_scripts' : [
		'cubew = cube.cube:main',
		]
	    },

	install_requires = [
	    'pcapy',
	    'pygame',
	    'OpenGL'
	    ],

	extras_require = {
	    'screenshot': ['PIL']
	    },

	package_data = {
	    'cube' : ['LICENSE', 'COPYING', 'screen.png']
	    },

	classifiers = [
	    'Development Status :: 4 - Beta',
	    'Environment :: Console',
	    'Environment :: MacOS X',
	    'Environment :: Win32 (MS Windows)',
	    'Environment :: X11 Applications',
	    'Intended Audience :: Information Technology',
	    'Intended Audience :: System Administrators',
	    'License :: DFSG approved',
	    'License :: OSI Approved :: GNU General Public License (GPL)',
	    'Operating System :: OS Independent',
	    'Programming Language :: Python',
	    'Natural Language :: English',
	    'Topic :: System :: Networking :: Monitoring',
	    'Topic :: Utilities',
	    'Topic :: Security'
	    ],

	author = 'Jeffrey Kyllo',
	author_email = 'jkyllo-cube@echospiral.com',
	description = 'Python implementation of the Spinning Cube of Potential Doom.',
	long_description = """
NetCube is a tool for visualizing network traffic in three dimensions.  It is
inspired by the `Spinning Cube of Potential Doom`__ and was originally developed
back in 2005.

__ http://www.nersc.gov/nusers/security/TheSpinningCube.php

NetCube requires:
 - pcapy (requires libpcap or winpcap)
 - OpenGL
 - pygame

It uses pcapy to capture packets via libpcap allowing the use of the same
filters used by tcpdump and part of Ethereal.  After capturing a packet, NetCube
adds it to a list to be rendered as a pixel within a 3d cube.  Each axis
corresponds to a different parameter of the packet.  At present these are the
source address, the destination address, and the port number.  The color of the
pixel corresponds to the vertical axis (port number) in order to make the
diagram more readable as it rotates.

Bug reports can be filed at the home page listed below.
	""",
	license = 'GPLv2',
	keywords = 'network,dump,cube,trace,OpenGL,pcap,capture',
	url = 'http://echospiral.com/trac/cube'
	)


	

