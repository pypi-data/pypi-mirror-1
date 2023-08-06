# Copyright (C) 2008 John Millikin. See LICENSE.txt for details.
# Author: John Millikin <jmillikin@gmail.com>

from decimal import Decimal
import array
import collections
import unittest
import UserList
import UserDict
import UserString
from .. import write, errors, util

class TestCase (unittest.TestCase):
	def w (self, value, expected, **kwargs):
		serialized = write (value, **kwargs)
		self.assertEqual (serialized, expected)
		self.assertEqual (type (serialized), type (expected))
		
class MiscTests (TestCase):
	def test_fail_on_unknown (self):
		self.assertRaises (errors.UnknownSerializerError, write,
		                   [object ()])
		
	def test_fail_on_unwrapped_atom (self):
		self.assertRaises (errors.WriteError, write, 1)
		
class WriteKeywordTests (TestCase):
	def test_null (self):
		self.w ([None], u'[null]')
		
	def test_true (self):
		self.w ([True], u'[true]')
		
	def test_false (self):
		self.w ([False], u'[false]')
		
class WriteNumberTests (TestCase):
	def test_int (self):
		self.w ([1], u'[1]')
		
	def test_long (self):
		self.w ([1L], u'[1]')
		
	def test_decimal (self):
		self.w ([Decimal ('1.1')], u'[1.1]')
		
	def test_long_float (self):
		# Value that will give different string representations
		# depending on whether it is passed to unicode() or repr().
		pi = 3.1415926535897931
		self.assertNotEqual (str (pi), repr (pi))
		self.assertNotEqual (unicode (pi), repr (pi))
		self.w ([pi], u'[3.1415926535897931]')
		
	def test_long_decimal (self):
		pi = Decimal ('3.1415926535897931')
		self.w ([pi], u'[3.1415926535897931]')
		
	def test_negative_zero (self):
		self.w ([-0.0], u'[-0.0]')
		
	def test_negative_zero_decimal (self):
		self.w ([Decimal ('-0.0')], u'[-0.0]')
		
	def test_complex (self):
		self.w ([5+0j], u'[5.0]')
		self.w ([5.5+0j], u'[5.5]')
		
	def test_fail_complex (self):
		self.assertRaises (errors.WriteError, write, [5+1j])
		
	def test_fail_on_infinity (self):
		self.assertRaises (errors.WriteError, write, [util.INFINITY])
		self.assertRaises (errors.WriteError, write, [Decimal ('Infinity')])
		
	def test_fail_on_neg_infinity (self):
		self.assertRaises (errors.WriteError, write, [-util.INFINITY])
		self.assertRaises (errors.WriteError, write, [Decimal ('-Infinity')])
		
	def test_fail_on_nan (self):
		self.assertRaises (errors.WriteError, write, [util.NAN])
		self.assertRaises (errors.WriteError, write, [Decimal ('NaN')])
		
class WriteArrayTests (TestCase):
	def test_empty_array (self):
		self.w ([], u'[]')
		
	def test_single_value_array (self):
		self.w ([True], u'[true]')
		
	def test_multiple_value_array (self):
		self.w ([True, True], u'[true,true]')
		
	def test_empty_indent (self):
		self.assertEqual (write ([True, True], indent = ''),
		                  u'[\ntrue,\ntrue\n]')
		
	def test_single_indent (self):
		self.assertEqual (write ([True, True], indent = '\t'),
		                  u'[\n\ttrue,\n\ttrue\n]')
		
	def test_nested_indent (self):
		self.assertEqual (write ([True, [True]], indent = '\t'),
		                  u'[\n\ttrue,\n\t[\n\t\ttrue\n\t]\n]')
		
	def test_generator (self):
		self.w ((_ for _ in (True, True)), u'[true,true]')
		
	def test_set (self):
		self.w (set (('a', 'b')), u'["a","b"]')
		
	def test_set_sorted (self):
		self.assertEqual (write (set (('e', 'm')), sort_keys = True),
		                  u'["e","m"]')
		
	def test_frozenset (self):
		self.w (frozenset (('a', 'b')), u'["a","b"]')
		
	def test_frozenset_sorted (self):
		self.assertEqual (write (frozenset (('e', 'm')), sort_keys = True),
		                  u'["e","m"]')
		
	def test_array (self):
		self.w (array.array('i', [1,2,3]), u'[1,2,3]')
		
	def test_deque (self):
		deq = collections.deque ((1, 2, 3))
		self.w (deq, u'[1,2,3]')
		
	def test_userlist (self):
		self.w (UserList.UserList ((1, 2, 3)), u'[1,2,3]')
		
	def test_fail_on_self_reference (self):
		a = []
		a.append (a)
		
		self.assertRaises (errors.WriteError, write, a)
		
class WriteObjectTests (TestCase):
	def test_empty_object (self):
		self.w ({}, u'{}')
		
	def test_single_value_object (self):
		self.w ({'a': True}, u'{"a":true}')
		
	def test_multiple_value_object (self):
		self.w ({'a': True, 'b': True}, u'{"a":true,"b":true}')
		
	def test_sort_keys (self):
		self.assertEqual (write ({'e': True, 'm': True},
		                         sort_keys = True),
		                  u'{"e":true,"m":true}')
		
	def test_empty_indent (self):
		self.assertEqual (write ({'a': True, 'b': True},
		                         sort_keys = True, indent = ''),
		                  u'{\n"a": true,\n"b": true\n}')
		
	def test_single_indent (self):
		self.assertEqual (write ({'a': True, 'b': True},
		                         sort_keys = True, indent = '\t'),
		                  u'{\n\t"a": true,\n\t"b": true\n}')
		
	def test_nested_indent (self):
		self.assertEqual (write ({'a': True, 'b': {'c': True}},
		                         sort_keys = True, indent = '\t'),
		                  u'{\n\t"a": true,\n\t"b": {\n\t\t"c": true\n\t}\n}')
		
	def test_fail_on_invalid_key (self):
		self.assertRaises (errors.WriteError, write, {1: True})
		
	def test_coerce_invalid_key (self):
		self.w ({1: True}, u'{"1":true}', coerce_keys = True)
		self.w ({True: 1}, u'{"true":1}', coerce_keys = True)
		self.w ({(): 1}, u'{"()":1}', coerce_keys = True)
		
	def test_defaultdict (self):
		defdict = collections.defaultdict (lambda: 9)
		defdict['a'] = 42
		self.w (defdict, u'{"a":42}')
		
	def test_userdict (self):
		self.w (UserDict.UserDict (a = 42), u'{"a":42}')
		
	def test_fail_on_self_reference (self):
		a = {}
		a['a'] = a
		
		self.assertRaises (errors.WriteError, write, a)
		
		del[a['a']]
		a['a'] = [a]
		
		self.assertRaises (errors.WriteError, write, a)
		
class WriteStringTests (TestCase):
	def test_empty_string (self):
		self.w ([''], u'[""]')
		
	def test_escape_quote (self):
		self.w (['"'], u'["\\""]')
		
	def test_escape_reverse_solidus (self):
		self.w (['\\'], u'["\\\\"]')
		
	def test_escape_solidus (self):
		self.w (['/'], u'["\\/"]')
		
	def test_escape_backspace (self):
		self.w (['\b'], u'["\\b"]')
		
	def test_escape_form_feed (self):
		self.w (['\f'], u'["\\f"]')
		
	def test_escape_line_feed (self):
		self.w (['\n'], u'["\\n"]')
		
	def test_escape_carriage_return (self):
		self.w (['\r'], u'["\\r"]')
		
	def test_escape_tab (self):
		self.w (['\t'], u'["\\t"]')
		
	def test_escape_control_characters (self):
		special_escapes = tuple ('\b\t\n\f\r')
		
		for code in range (0x0, 0x1F + 1):
			char = unichr (code)
			if char not in special_escapes:
				expected = u'["\\u%04x"]' % code
				self.w ([char], expected)
				
	def test_unicode_passthrough (self):
		self.w ([u'\u00B6\u00D7'], u'["\u00b6\u00d7"]', ascii_only = False)
		self.w ([u'\u24CA'], u'["\u24ca"]', ascii_only = False)
		self.w ([u'\U0001D11E'], u'["\U0001D11E"]', ascii_only = False)
		
	def test_escape_short_unicode (self):
		# Some Latin-1
		self.w ([u'\u00B6\u00D7'], u'["\\u00b6\\u00d7"]')
		
		# Higher planes
		self.w ([u'\u24CA'], u'["\\u24ca"]')
		
	def test_escape_long_unicode (self):
		# Should break into two UTF-16 codepoints
		self.w ([u'\U0001D11E'], u'["\\ud834\\udd1e"]')
		
	def test_userstring (self):
		self.w ([UserString.UserString ('test')], u'["test"]')
		
class WriteSubclassTests (TestCase):
	def test_int_subclass (self):
		class MyInt (int):
			pass
		self.w ([MyInt (10)], u'[10]')
		
