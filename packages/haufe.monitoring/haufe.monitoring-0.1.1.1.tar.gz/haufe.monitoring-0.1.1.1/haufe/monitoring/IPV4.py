# Copyright (c) 2008 - ALBAR (Toulouse, FRANCE).
# mailto:barthe@albar.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# Use epydoc (http://epydoc.sourceforge.net) to produce the documentation.
"""This module allows an easy manipulation of IPV4 addresses.

Quick start
===========

	>>> from IPV4 import IPV4
	>>> a = IPV4('192.168.1.3')
	>>> a			# a is a string
	'192.168.1.3'
	>>> a.set_mask(23) # same as a = IPV4('192.168.1.3/23')
	>>> a.mask         # or a = IPV4('192.168.1.3', '255.255.254.0')
	'255.255.254.0'
	>>> a.subnet.start
	'192.168.0.0'
	>>> a.subnet.end
	'192.168.1.255'
	>>> a.same_subnet('192.168.2.1')
	False
	>>> a.bitstr
	'11000000101010000000000100000011'
	>>> a.subnet.bitmask
	'11000000101010000000000'
	>>> a.hexaval  
	'c0a80103'
	>>> a.intval
	3232235779L
	>>> a.IPclass
	'C'
	
Description
===========

This module gives some utilities for IPV4 addresses. 

It defines the B{L{IP}}, B{L{Mask}} and B{L{Subnet}} classes. Objects of these classes should not be created
directly, but rather through the function B{L{IPV4}}. It defines also some useful conversion functions.

@requires: BitVector module (U{http://cobweb.ecn.purdue.edu/~kak/dist/BitVector-1.4.html})

@version:	0.1
@status:	beta
@author:    A. Barthe
@copyright: 2008 - ALBAR (Toulouse, FRANCE)
@contact:   mailto:barthe@albar.fr

"""

import re, types

########################################################################
#{ Constants
#: Regular expression to match a regular IP address (like 192.168.2.1)
RE_IP = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
#: Regular expression to match a an IP address with its mask  (like 192.168.2.1/24)
RE_SUBNET = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$')
#: Regular expression to match a hexadecimal IP address (like c0:a8:01:40 or OxC0A80140L)
RE_HEXA = re.compile('(?:0x)?(' + '[\.:]?'.join(['[0-9a-f]{2}'] * 4) + ')l?$')
#}
#{ Factory function
########################################################################
def IPV4(string, mask=''):
	"""The factory function for IP objects.
	@param string: a string that may have 3 forms:
		- a regular IP address like 192.168.2.1
		- a IP addresse with its mask like 192.168.2.1/24
		- a hexadecimal address like c0:a8:01:40 or 0xC0A80140L
	@param mask: an optional mask as an integer from 0 to 32 or as
		a regular IP address like 255.255.255.0
	@return: an L{IP} or L{Mask} object. 
		If an address appears to be a valid mask address, it is considered as is and a
		I{Mask} object is returned.
	@raise MalformedIP: wrong parameter.
	"""
	if type(string) is not types.StringType:
		raise MalformedIP('Invalid IP address: %s' % string)
	m = RE_HEXA.match(string.lower())
	if m is not None:
		result = IP(hexa2ip(re.sub('[\.:]', '', m.group(1))))
	elif RE_IP.match(string) and IP.check(string):
		result = IP(string)
	elif RE_SUBNET.match(string):
		ip, mask = string.split('/')
		result = IP(ip)
	else:
		raise MalformedIP('Invalid IP address: %s' % string)
	
	# Si l'IP est un masque valide, on la considere comme telle
	if Mask.check(result):
		return Mask(result)
	if mask != '':
		if RE_IP.match(mask) and Mask.check(mask):
			result.set_mask(Mask(mask))
		else:
			try:
				mask = int2maskip(int(mask))
				assert Mask.check(mask) is True
				result.set_mask(Mask(mask))
			except AssertionError, ValueError:
				raise MalformedIP('Invalid mask address: %s' % mask)
	return result
#}

#-----------------------------------------------------------------------
def _cache_attr(f):
	"Decorator that caches property values in attributes"
	def g(self, *args, **kwargs):
		attname = '_' + f.__name__
		if hasattr(self, attname):
			return getattr(self, attname)
		result = f(self, *args, **kwargs)
		setattr(self, attname, result)
		return result
	g.__doc__ = f.__doc__
	g.__dict__.update(f.__dict__)
	g.__name__ = f.__name__
	g.__undecorated__ = f
	return g
	
#{ Exceptions
########################################################################
class MalformedIP(Exception):
	"This exception is raised when the syntax of an IP is not recognized"
#}

########################################################################
class IP(str):
	"""This class is a subclass of the B{string builtin type} and the value of an IP
instance is always a regular IP address, even if it has been created
another way:

	>>> i = IPV4('192.168.2.1/24')
	>>> i
	'192.168.2.1'
	>>> i = IPV4('0xC0A80140L')
	>>> i
	'192.168.1.64'

Standard comparison methods are redefined to allow numeric comparison between IP addresses.
	"""
#{Comparison functions
	def __lt__(self, other):
		return self.intval < other.intval
		
	def __gt__(self, other):
		return self.intval > other.intval
		
	def __le__(self, other):
		return self.intval <= other.intval
		
	def __ge__(self, other):
		return self.intval >= other.intval
#}
#-----------------------------------------------------------------------
	def add(self, number):
		"""Addition function
		@param number: an B{integer} (not an IP object)
		@return: a new IP object.
		@raise MalformedIP: overflow
		"""
		return IPV4(int2ip(self.intval + number))
	
#-----------------------------------------------------------------------
	def sub(self, number):
		"""Substraction function
		@param number: an B{integer} (not an IP object)
		@return: a new IP object.
		@raise MalformedIP: overflow
		"""
		return IPV4(int2ip(self.intval - number))
	
#-----------------------------------------------------------------------
	@staticmethod
	def check(string):
		"Check that fields of the IP are less than 255"
		for i in string.split('.'):
			if int(i) > 255: return False
		return True
	
#-----------------------------------------------------------------------
	@property
	@_cache_attr
	def hexaval(self):
		"Returns the hexadecimal value"
		return ip2hexa(self)
	
	@property
	@_cache_attr
	def intval(self):
		"Returns the integer value"
		return int(self.hexaval, 16) 
	
	@property
	@_cache_attr
	def bitstr(self):
		"""Returns the bit string of the IP, like 
'11000000101010000000001000000001'"""
		return ip2bitstr(self) 
	
	@property
	@_cache_attr
	def IPclass(self):
		"Returns the IP class as a capital letter, e.g. 'C'"
		if self.bitstr.startswith('0'):
			return 'A'
		if self.bitstr.startswith('10'):
			return 'B'
		if self.bitstr.startswith('110'):
			return 'C'
		if self.bitstr.startswith('1110'):
			return 'D'
		if self.bitstr.startswith('1111'):
			return 'E'
		return None
	
#-----------------------------------------------------------------------
	def set_mask(self, mask):
		"""Sets the B{mask} and B{subnet} attributes of the IP.
		@param mask: either an integer lower or equal to 32, or
		as a regular IP adress, such as C{255.255.255.0}.
		@return: nothing
		@raise MalformedIP: wrong parameter.
		"""
		if type(mask) is types.IntType and mask <= 32:
			mask = Mask(int2maskip(mask))
		elif type(mask) is not Mask:
			mask = IPV4(mask)
			if type(mask) is not Mask:
				raise MalformedIP('Invalid mask address: %s' % mask)
		self.mask = mask
		self.subnet = Subnet(self, mask)
	
#-----------------------------------------------------------------------
	def iter(self, start=None, end=None):
		"""Returns an iterator that yields IP objects. Both start and end 
		optional parameters may be IP objects or strings to create an IP with.
		@param start: the first value. By default: the IP itself.
		@param end: the last value. By default the last adress of the L{Subnet} if it
		exists, or 255.255.255.255.
		@returns: an iterator of IP objects.
		@raise MalformedIP: wrong parameter.
		"""
		if start is None: 
			start = self
		elif type(start) is types.StringType:
			start = IPV4(start)
		if end is None:
			try:
				end = self.subnet.end
			except AttributeError:
				end = IP('255.255.255.255')
		elif type(end) is types.StringType:
			end = IPV4(end)
		current = start
		while current <= end:
			yield current
			current = current.add(1)
		
#-----------------------------------------------------------------------
	def same_subnet(self, ip):
		"""Is the ip parameter in the same subnet than the IP object ?
		If both of the IP object and the ip parameter have no subnet, then the answer is False.
		@param ip: IP object or string
		@return: boolean
		@raise MalformedIP: wrong parameter.
		"""
		if type(ip) is types.StringType:
			ip = IPV4(ip)
		if not hasattr(self, 'subnet'):
			if not hasattr(ip, 'subnet'):
				return False
			return ip.subnet.contains(self)
		return self.subnet.contains(ip)
	
	
########################################################################
class Mask(IP):
	"Subclass of IP."
	@staticmethod
	def check(string):
		"Check the mask validity."
		return re.match('1+0*$', ip2bitstr(string)) is not None

#-----------------------------------------------------------------------
	@property
	@_cache_attr
	def bitnumber(self):
		"Returns the number of '1' bits" 
		return mask_bitnumber(self) 
	

########################################################################
class Subnet(object):
	"This class represent a subnet as the association of an IP and a Mask"
	def __init__(self, ip, mask):
		"""@param ip: an IP object
		@param mask: a Mask object"""
		self.ip, self.mask = ip, mask
	
#-----------------------------------------------------------------------
	@property
	@_cache_attr
	def bitmask(self):
		"@return: the bitmask as a bit string."
		return self.ip.bitstr[0:self.mask.bitnumber] 
		
	@property
	@_cache_attr
	def start(self):
		"@return: the first address of the subnet, as a IP object'."
		return IP(bitstr2ip(rpad(self.bitmask, '0', 32))) 
		
	@property
	@_cache_attr
	def end(self):
		"@return: the last address of the subnet, as a IP object'."
		return IP(bitstr2ip(rpad(self.bitmask, '1', 32))) 
		
#-----------------------------------------------------------------------
	def contains(self, ip):
		"""Does the ip belong to the subnet ?
		@param ip: a IP object
		@return: boolean"""
		return ip.bitstr.startswith(self.bitmask)


########################################################################
########################################################################
from BitVector import BitVector

#{ Conversion functions
#-----------------------------------------------------------------------
def bitstr2ip(bitstr):
	"""Converts a bit string to a regular IP.
	@param bitstr: an IP as a bit string
	@return: a regular IP as a string"""
	return '.'.join([ str(int(BitVector(bitstring=x))) for x in fl_split(bitstr, 8) ])

#-----------------------------------------------------------------------
def ip2bitstr(ip):
	"""Converts a regular IP to a bit string
	@param ip: a regular IP as a string
	@return: the IP as a bit string"""
	return ''.join([ str(BitVector(intVal=int(x), size=8)) for x in ip.split('.') ])

#-----------------------------------------------------------------------
def hexa2ip(hexstr):
	"""Converts a hexadecimal address to a regular IP.
	@param hexstr: a hexadecimal address as a string (without any extra character)
	@return: a regular IP as a string"""
	return '.'.join([ str(int(x, 16)) for x in fl_split(hexstr, 2) ])

#-----------------------------------------------------------------------
def ip2hexa(ip):
	"""Converts a regular IP to a hexadecimal address.
	@param ip: a regular IP as a string
	@return: a hexadecimal address as a string"""
	return ''.join([ '%02x' % int(x) for x in ip.split('.') ])

#-----------------------------------------------------------------------
def int2ip(value):
	"""Converts an integer value to a regular IP.
	@param value: the integer
	@return: a regular IP as a string"""
	return hexa2ip('%08x' % value)
#}

#{ Bitmask functions
#-----------------------------------------------------------------------
def int2maskip(value):
	"""Converts a integer less than 32 to a regular IP.
	@param value: the integer
	@return: a regular IP as a string"""
	assert value <= 32
	bitstr = rpad('1' * value, '0', 32)
	return bitstr2ip(bitstr)

#-----------------------------------------------------------------------
def mask_bitnumber(mask):
	"""Returns the mask as its number of '1' bits.
	@param mask: a regular IP as a string
	@return: integer"""
	return ip2bitstr(mask).count('1')
#}

#{ Miscelaneous functions
#-----------------------------------------------------------------------
def fl_split(string, size=8):
	"""Fixed-length split.
	@param string: string to be splitted
	@param size: the length of the pieces. The length of the string
	must be divisible by the size.
	@return: a list of strings
	"""
	assert len(string) % size == 0
	return [ string[i:i+size] for i in range(0, len(string), size) ]

#-----------------------------------------------------------------------
def rpad(string, padding_char, length):
	"""Pads a string at right hand with I{padding_char} up to I{length}.
	@param string: the string to be padded.
	@param padding_char: the character to pad with
	@param length: the length of the resulting string. Must be lesser or equal than
	the length of I{string}.
	@return: the padded string"""	
	assert len(string) <= length
	return string + padding_char * (length - len(string))
#}

########################################################################
if __name__ == '__main__':
	import sys
	for ip in sys.argv[1:]:
		i = IPV4(ip)
		print """
IPaddress: %s
	Hexa: %s
	Int: %d
	Bits: %s 
	Class: %s""" % (i, i.hexaval, i.intval, i.bitstr, i.IPclass)
		try:
			print """	Mask: %s
	Subnet starts at %s
	Subnet ends at %s""" % (i.mask, i.subnet.start, i.subnet.end)
		except AttributeError: 
			print "	Mask: None"
		
