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


"""A module for the reading and parsing of network packets.  This module can be
used for various levels of control from parsing low level ethernet frames to
reading completely parsed packets into nested dictionaries."""


import pcapy
import socket
import struct
import re
import string

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

def signed32bit_to_unsigned(input):
    """Converts the "negative bit" on a signed integer into the unsigned most-significant bit on an unsigned integer.  This is so that int(a_signed_int) does not result in an unsigned, but extremely large integer when the intent is simply to read an unsigned int from a buffer of bytes."""
    unsignedint = input
    if input & 2**31:
	unsignedint = (input & (2**31-1)) + 2**31

    return unsignedint





def decode_ethernet_frame(s):
    """Decode the data provided as an Ethernet frame.  This function returns a
    dictionary of values parsed from that frame:
	source:		    The source MAC address of this frame
	destination:	    The destination MAC address of this frame
	type:		    The frame type (Ethernet II)
	ethernet_type:	    The Ethernet type
	data:		    The data field of this frame
	fcs:		    The FCS field of this frame

    If the frame is a VLAN frame then the following apply.
	vlan_priority:	    The VLAN priority 
	vlan_cfi
	vlan_vid
    """
    d={}

    #print "len(s)=%s" % len(s)

    # We want Ethernet II packets
    type=socket.ntohs(struct.unpack('H', s[12:14])[0])
    if type > 1500:
	t = 0
	for i in range(0, 6, 2):
	    t <<= 16
	    t = struct.unpack('H', s[i:i+2])[0]
	    #print "t=%s" % t
	#d['source']=socket.ntohs(struct.unpack('H', s[0:6])[0])
	#d['destination']=socket.ntohs(struct.unpack('H', s[6:12])[0])
	d['type']='Ethernet II'
	d['ethernet_type']=s[12:14]
	d['data']=s[14:60]
	d['fcs']=s[60:64]

	# parse vlan information if this is a 802.1Q frame
	if type == 8100:
	    d['vlan_priority']=s[64:67]
	    d['vlan_cfi']=s[67:68]
	    d['vlan_vid']=s[68:80]
    else:
	d['type']='Ethernet 802.3'
	#d['len']=socket.ntohs(struct.unpack('H', s[12:14])[0])
	d['len']=type

	#print "------------------------------------------------"
	#print "Read 802.3 ethernet frame which is currently not supported."
	#print "frame length=%d" % len(s)
	#print "d['len']=%d" % d['len']
	text = ""
	i = 0
	for c in s:
	    h = "0" + ("%x" % ord(c))
	    h = h[len(h)-2:len(h)]
	    text += h
	    i += 1
	    if i % 16 == 0:
		text += "\n"
		i = 0
	    elif i % 4 == 0:
		text += "    "
	    else:
		text += " "

	#print "packet:"
	#print text
	#print "------------------------------------------------"

    return d

def int_to_dottedquad(n):
    """Takes a 32 bit integer and converts it into a IPv4 dotted quad."""
    val = n
    ret = []
    for i in range(4):
	ret.append(str(val & 2**8-1))
	val >>= 8
    ret.reverse()
    return string.join(ret, '.')

def bytes_to_int(s):
    """Reads four bytes into an unsigned integer."""
    ip = socket.ntohl(struct.unpack('I',s)[0])
    ip = signed32bit_to_unsigned(ip)
    return ip

def dottedquad_to_int(s):
    """Converts an IPv4 dotted quad into an integer.  Not yet implemented."""
    import re
    r = re.compile('')

def decode_ip_packet(s):
    """Decode the data provided as an IP packet.  This function returns a
    dictionary of values parsed from that packet:

	version:	    	The IP version (4, 6, etc.)
	header_len:	    	The length of the IP header.
	tos:		    	The Type of Service field.
	total_len:	    	The total length of the packet.
	id:		    	Packet fragment identifier.
	flags:			The IP flags of this packet.
	fragment_offset:	Offset within the set of fragments(?).
	ttl:			The Time to Live of this packet.
	protocol:		Identifier of the contained protocol.
	checksum:		16 bit one's complement checksum.
	source_address:		The IP address of the source node.
	destination_address:	The IP address of the destination node.

	source_address_n:	The IP address of the source node (int).
	destination_address_n:	The IP address of the destination node (int).
	options:		The IP options for this packet.
	data:			The encapsulated data of this packet.
    """
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

    source = bytes_to_int(s[12:16])
    dest = bytes_to_int(s[16:20])
    
    d['source_address_n'] = source
    d['destination_address_n'] = dest

    if d['header_len']>5:
	d['options']=s[20:4*(d['header_len']-5)]
    else:
	d['options']=None
    d['data']=s[4*d['header_len']:]
    return d

def decode_tcp_packet(s):
    """Decode the data provided as an TCP packet.  This function returns a
    dictionary of values parsed from that packet:

	source_port:		    The source port of the related socket.
	destination_port:	    The destination port of the related socket.
	sequence_number:	    The sequence number of this packet.
	acknowledgement_number:	    The acknowledgement number of this packet.
	data_offset:		    The offset to the data in this packet.
	reserved
	flags:			    The TCP flags for this packet.
	window:			    The sliding window for this packet.
	checksum:		    The checksum.
	urgent_pointer:
	options:		    The TCP options for this packet.
	padding:		    Padding to round of the header.
	data:			    The data contained in this packet.
    """
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
	tempstring = s[20:24]
	if len(tempstring) == 4:
	    d['options']=struct.unpack('I', s[20:24])[0] & 0x0fff
    if len(s) > 24:
	d['padding']=ord(s[24])
	d['data']=s[25:]

    return d

def decode_udp_packet(s):
    """Decode the data provided as an TCP packet.  This function returns a
    dictionary of values parsed from that packet:
	source_port:		    The source port of the datagram.
	destination_port:	    The destination port of the datagram.
	length:			    The length of the packet (data?).
	checksum:		    The checksum.
	data:			    The data contained in this packet.
    """
    d={}
    
    d['source_port']=struct.unpack('H', s[1:3])[0]
    d['destination_port']=struct.unpack('H', s[3:5])[0]
    d['length']=struct.unpack('H', s[5:7])[0]
    d['checksum']=struct.unpack('H', s[7:9])[0]
    d['data']=s[9:]

    return d
   

def iprange(cidr):
    """Calculate the low and high IP addresses of a given CIDR range and return
    them as 32 bit unsigned integers."""

    t = re.split("\/", cidr)
    range_mask = 2**32 - 2**(32-int(t[1]))
    ip = socket.ntohl(struct.unpack('I', socket.inet_aton(t[0]))[0])
    low = signed32bit_to_unsigned(ip & range_mask)
    high = signed32bit_to_unsigned(ip | (range_mask ^ 2**32-1))
    return (low, high)
    

def listinterfaces():
    """Print out a list of interfaces available for capture."""
    import sys
    interfaces = pcapy.findalldevs()
    for index in range(len(interfaces)):
	print "%s => %s" % (index, interfaces[index])
    sys.exit()

class PacketReader(object):
    """Configures a packet capturing session and allows a simple read of those
    packets.  Can be set for blocking or non-blocking IO.  The following member
    variables can be set to adjust the behavior of the object:

	readfile:	The pcap file to read packets from.
	writefile:	The pcap file to which to write captured packets.
	promisc:	Boolean setting whether to use promiscuous capture.
	interface:	The name of the interface from which to capture.
	filter:		The pcap filter to use for filtering packets.
	timeout:	In non-blocking mode, the amount of time to wait for
			    packets during each read
	snaplen:	The number of bytes to read from each packet.
	maxcount:	In non-blocking mode, the _maximum_ number of packets
			    to read.  In blocking mode, the number of packets
			    to wait for before returning any packets.
	nonblock:	Turn on non-blocking mode.
	"""
	
    def __init__(self, readfile=None, writefile=None, promisc=False, interface=None, filter=None, timeout=100, snaplen=68, maxcount=0, nonblock=False):
	"""Create a new PacketReader, overriding default settings if given."""
	self.readfile = readfile
	self.writefile = writefile
	self.promisc = promisc
	self.interface = interface

	interfaces = pcapy.findalldevs()
	self.filter = filter
	self.timeout = timeout
	self.snaplen = snaplen
	self.maxcount = maxcount
	self.nonblock = nonblock

	if len(self.interface) > 0:
	    # See if that's a valid interface
	    if self.interface not in interfaces:
		# Nope!  Let's see if it's a number index
		isint = True
		try:
		    index = int(self.interface)
		except ValueError:
		    # Nope!
		    isint = False

		if isint:
		    # Conversion was successful, let's try it
		    if index >= 0 and index < len(interfaces):
			self.interface = interfaces[index]
		else:
		    print "Interface specified doesn't exist!"
		    print "Looking up interface..."
		    self.interface = pcapy.lookupdev()
		    print "Using default interface: %s" % self.interface

	else:
	    print "Looking up interface."
	    self.interface = pcapy.lookupdev()

	#print "PacketReader.interface=%s" % self.interface

	self.reader = None
	self.writer = None

    def getnet(self):
	"""Read the network address from the capture device."""
	if self.reader is not None:
	    return self.reader.getnet()

    def getmask(self):
	"""Read the network mask from the capture device."""
	if self.reader is not None:
	    return self.reader.getmask()

    def setup(self):
	"""Apply the settings (in member variables) to the current capture
	sessions.  This allows a capture session to be reset and start off with
	new parameters."""
	if self.readfile is not None and len(self.readfile) > 0:
	    self.reader = pcapy.open_offline(self.readfile)
	else:
	    if self.interface is None or self.interface not in pcapy.findalldevs():
		self.interface = pcapy.lookupdev()

	    if self.promisc:
		p = 1
	    else:
		p = 0

	    #print "Opening device with permiscuous=%s" % p

	    self.reader = pcapy.open_live(self.interface, self.snaplen, p, self.timeout)

	if self.filter is not None and len(self.filter) > 0:
	    try:
		self.reader.setfilter(self.filter)
	    except pcapy.PcapError, e:
		print "Invalid pcap filter: %s" %  self.filter

	if self.writefile is not None and len(self.writefile) > 0:
	    self.writer = self.reader.dump_open(self.writefile)
	
	if self.nonblock:
	    nonblock = 1
	else:
	    nonblock = 0
	self.reader.setnonblock(nonblock)

    def read(self, count=0):
	"""Reads packets from the configured capture source.  If in non-blocking mode then count is the maximum number of packets to return.  If in blocking mode then count is the number of packets to wait for before returning."""
	packets = []

	def packet_read(header, data):
	    packets.append((header, data))

	if self.nonblock:
	    status = self.reader.dispatch(count, packet_read)
	else:
	    status = self.reader.loop(count, packet_read)

	return packets

class ParsedPacketReader(object):
    """Reads packets from a PacketReader as necessary and parses them into
    nested dictionaries of protocol values."""
    def __init__(self, preader):
	"""Initialize a new ParsedPacketReader and use preader as the source of
	network packets."""
	self.preader = preader

    def read(self, count=0):
	"""Read packets from the packet source, parse them, and return them in a list.  count is passed on to PacketReader.read()."""
	return [self.parse(h, d) for h, d in self.preader.read(count)]

    def parse(self, header, data):
	"""Parse the given packet header and packet data into nested dictionaries with values from the protocols in the packet."""
	ret = {}
	ret['raw_header'] = header
	ret['raw_data'] = data

	if data is None:
	    raise Exception('PacketParser.parse: data not set.')

	frame = decode_ethernet_frame(data)
	ret['frame'] = frame
	if frame.has_key('type') and frame['type'] == 'Ethernet II':
	    if frame['ethernet_type'] == '\x08\x00':
		packet = data[14:]
	    elif frame['ethernet_type'] == '\x18\x00':
		packet = data[16:]
	    else:
		return

	    decoded = decode_ip_packet(packet)
	    ret['ip_packet'] = decoded

	    # TCP
	    if decoded['protocol'] == socket.IPPROTO_TCP:
	    	decoded['tcp_packet'] = decode_tcp_packet(decoded['data'])

	    # UDP
	    elif decoded['protocol'] == socket.IPPROTO_UDP:
		decoded['udp_packet'] = decode_udp_packet(decoded['data'])

	return ret
