# Copyright (C) 2008 John Millikin. See LICENSE.txt for details.
# Author: John Millikin <jmillikin@gmail.com>

"""Implements jsonlib.write"""

from decimal import Decimal
from .util import memoized, KEYWORDS
from . import errors

__all__ = ['write']

ESCAPES = {
	'"': '\\"',
	'\t': '\\t',
	'\b': '\\b',
	'\n': '\\n',
	'\r': '\\r',
	'\f': '\\f',
	'/': '\\/',
	'\\': '\\\\'
}

def write_array (value):
	"""Serialize an iterable to a list of strings in JSON array format."""
	retval = ['[']
	
	for index, item in enumerate (value):
		if item is value:
			raise errors.WriteError ("Can't write self-referential values")
		retval.extend (_write (item))
		if (index + 1) < len (value):
			retval.append (', ')
	retval.append (']')
	return retval
	
def write_object (value):
	"""Serialize a mapping to a list of strings in JSON object format."""
	retval = ['{']
	
	for index, (key, sub_value) in enumerate (value.items ()):
		if not isinstance (key, (str, unicode)):
			raise errors.WriteError ("Only strings may be used as object keys")
			
		if sub_value is value:
			raise errors.WriteError ("Can't write self-referential values")
			
		retval.extend (_write (key))
		retval.append (': ')
		retval.extend (_write (sub_value))
		if (index + 1) < len (value):
			retval.append (', ')
	retval.append ('}')
	return retval
	
@memoized
def write_char (char):
	"""Serialize a single unicode character to its JSON representation."""
	if char in ESCAPES:
		return ESCAPES[char]
		
	# Control character
	if ord (char) in range (0x0, 0x1F + 1):
		return '\\u%04x' % ord (char)
		
	# Unicode
	if ord (char) > 0x7E:
		# Split into surrogate pairs
		if ord (char) > 0xFFFF:
			unicode_value = ord (char)
			reduced = unicode_value - 0x10000
			second_half = (reduced & 0x3FF) # Lower 10 bits
			first_half = (reduced >> 10)
			
			first_half += 0xD800
			second_half += 0xDC00
			
			return '\\u%04x\\u%04x'% (first_half, second_half)
		else:
			return '\\u%04x' % ord (char)
			
	return char.encode ('ascii')
	
@memoized
def write_string (value):
	"""Serialize a string to its JSON representation.
	
	This function will use the default codec for decoding the input
	to Unicode. This might raise an exception and halt the entire
	serialization, so you should always use unicode strings instead.
	
	"""
	return write_unicode (unicode (value))
	
@memoized
def write_unicode (value):
	"""Serialize a unicode string to its JSON representation."""
	return ['"'] + [write_char (char) for char in value] + ['"']
	
# Fundamental types
_m_str = memoized (str)
TYPE_MAPPERS = {
	dict: write_object,
	unicode: write_unicode,
	str: write_string,
	list: write_array,
	tuple: write_array,
	int: _m_str,
	long: _m_str,
	float: _m_str,
	Decimal: _m_str,
	type (True): (lambda val: 'true' if val else 'false'),
	type (None): lambda _: 'null',
}

def _write (value):
	"""Serialize a Python value into a list of byte strings.
	
	When joined together, result in the value's JSON representation.
	
	"""
	v_type = type (value)
	try:
		return TYPE_MAPPERS[v_type] (value)
	except KeyError:
		# Might be a subclass
		for mapper_type, mapper in TYPE_MAPPERS.items ():
			if isinstance (value, mapper_type):
				return mapper (value)
				
		raise errors.UnknownSerializerError (value)
		
def write (value):
	"""Serialize a Python value to a JSON-formatted byte string."""
	return ''.join (_write (value))
	
