#!/usr/bin/python2.5
#
# Copyright 2009, Robert M. Pufky (robert.pufky@gmail.com)
#
# GPLv2 License:
# --------------
# Copyright (C) 2009 Robert M. Pufky (robert.pufky@gmail.com)
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details.
#
# You should have received a copy of the GNU General Public License along with 
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
#
# You can also read the license at:
#
#  http://www.opensource.org/licenses/gpl-2.0.php
#
# Please contact me if you wish to use this in another product that you are 
# building (robert.pufky@gmail.com); or building to sell.
#
"""Test suite for option interface."""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'

import unittest
import options


class OptionTestData(object):
  """Basic option test data."""
  INT_TYPES = [int(), None]
  BOOL_TYPES = [bool(), None]
  STRING_TYPES = [str(), unicode(), None]
  FLOAT_TYPES = [float(), None]
  TYPE_INT_TYPES = map(lambda x: type(x), INT_TYPES)
  TYPE_BOOL_TYPES = map(lambda x: type(x), BOOL_TYPES)
  TYPE_STRING_TYPES = map(lambda x: type(x), STRING_TYPES)
  TYPE_FLOAT_TYPES = map(lambda x: type(x), FLOAT_TYPES)
  LONG = '--long'
  SHORT = '-l'
  DEFAULT = 1
  FLOAT_DEFAULT = 1.0
  STRING_DEFAULT = 'a'
  DESCRIPTION = 'option'
  VALUE = 3
  SET_DEFAULT = 'mkv'
  SET_LIST = ['acc', 'mp4', 'divx', 'mkv']
  LOW = 1
  HIGH = 10


class TestAbstractOptionClass(unittest.TestCase):
  """Verifies the Abstracted Option class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.Option(self.data.LONG, self.data.SHORT,
                                 self.data.DESCRIPTION, self.data.DEFAULT,
                                 self.data.INT_TYPES)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testDefaultOption(self):
    """Verifies default Option class is constructed properly."""
    self.assertEqual(self.option.long, self.data.LONG)
    self.assertEqual(self.option.short, self.data.SHORT)
    self.assertEqual(self.option.default, self.data.DEFAULT)
    self.assertEqual(self.option.value, self.data.DEFAULT)
    self.assertEqual(self.option.description, self.data.DESCRIPTION)

  def testOptionWithValue(self):
    """Verifies Option class with value is constructed properly."""
    self.option = options.Option(self.data.LONG, self.data.SHORT,
                                 self.data.DESCRIPTION, self.data.DEFAULT,
                                 self.data.INT_TYPES, self.data.VALUE)
    self.assertEqual(self.option.long, self.data.LONG)
    self.assertEqual(self.option.short, self.data.SHORT)
    self.assertEqual(self.option.default, self.data.DEFAULT)
    self.assertEqual(self.option.value, self.data.VALUE)
    self.assertEqual(self.option.description, self.data.DESCRIPTION)

  def testCommandDefaultArgs(self):
    """Verifies an empty command list is generated successfully."""
    self.assertEqual([], self.option.Command())
    self.assertEqual([], self.option.Command(short=True))

  def testCommandNonDefaultArgs(self):
    """Verifies command list with non-default arguments is generated."""
    self.option.SetValue(self.data.VALUE)
    self.assertEqual([self.data.LONG, str(self.data.VALUE)],
                     self.option.Command())
    self.assertEqual([self.data.SHORT, str(self.data.VALUE)],
                     self.option.Command(short=True))

  def testCheckType(self):
    """Verifies datatype checking works properly."""
    self.assertTrue(self.option._CheckType(self.data.VALUE))
    self.assertTrue(self.option._CheckType(None))
    self.assertFalse(self.option._CheckType(4.5))

  def testString(self):
    """Verifies the String conversion of Option is correct."""
    option_str = (
        "(Long: '%s', Short: '%s', Description: '%s', Default: %s, "
        'DataTypes: %s, Value: %s)' %
        (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
         self.data.DEFAULT, self.data.TYPE_INT_TYPES, self.data.DEFAULT))
    self.assertEqual(str(self.option), option_str)

  def testRepr(self):
    """Verifies the String representation of Option is correct."""
    option_repr = (
        "options.Option('%s', '%s', '%s', %s, %s, %s)" %
        (self.data.LONG, self.data.SHORT,
         self.data.DESCRIPTION, self.data.DEFAULT, self.data.TYPE_INT_TYPES,
         self.data.DEFAULT))
    self.assertEqual(repr(self.option), option_repr)


class TestAllTypesAbstractOptionClass(unittest.TestCase):
  """Verifies the Abstracted Option with all primatives class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.AllTypesOption(self.data.LONG, self.data.SHORT,
                                         self.data.DESCRIPTION)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testInteger(self):
    """Verifies Integers are accepted properly."""
    self.option.SetValue(1)

  def testLong(self):
    """Verifies Longs are accepted properly."""
    self.option.SetValue(1L)

  def testFloat(self):
    """Verifies Floats are accepted properly."""
    self.option.SetValue(1.0)

  def testString(self):
    """Verifies Strings are accepted properly."""
    self.option.SetValue('1')

  def testUnicode(self):
    """Verifies Unicode is accepted properly."""
    self.option.SetValue(u'1')

  def testBoolean(self):
    """Verifies Booleans are accepted properly."""
    self.option.SetValue(True)

  def testNone(self):
    """Verifies None is accepted properly."""
    self.option.SetValue(None)


class TestBooleanOptionClass(unittest.TestCase):
  """Verifies the BooleanOption class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.BooleanOption(self.data.LONG, self.data.SHORT,
                                        self.data.DESCRIPTION)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testBooleanFalseOption(self):
    """Verifies a non-enabled Boolean Option works properly."""
    self.assertEqual([], self.option.Command())

  def testBooleanTrueOption(self):
    """Verifies an enabled Boolean Option works properly."""
    self.option.SetValue(True)
    self.assertEqual([self.data.LONG], self.option.Command())
    self.assertEqual([self.data.SHORT], self.option.Command(short=True))

  def testNonBooleanOption(self):
    """Verifies a non-boolean or non-None value fails properly."""
    self.assertRaises(TypeError, self.option.SetValue, '1')

  def testString(self):
    """Verifies the String conversion of BooleanOption is correct."""
    option_str = (
        "(Long: '%s', Short: '%s', Description: '%s', Default: %s, "
        'DataTypes: %s, Value: %s)' %
        (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
         None, self.data.TYPE_BOOL_TYPES, None))
    self.assertEqual(str(self.option), option_str)

  def testRepr(self):
    """Verifies the String representation of BooleanOption is correct."""
    option_repr = (
        "options.BooleanOption('%s', '%s', '%s', %s, %s, %s)" %
        (self.data.LONG, self.data.SHORT,
         self.data.DESCRIPTION, None, self.data.TYPE_BOOL_TYPES,
         None))
    self.assertEqual(repr(self.option), option_repr)


class TestIntegerOptionClass(unittest.TestCase):
  """Verifies the IntegerOption class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.IntegerOption(self.data.LONG, self.data.SHORT,
                                        self.data.DESCRIPTION,
                                        self.data.DEFAULT)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testBadIntegerDefaultOption(self):
    """Verifies a bad Integer default works properly."""
    self.assertRaises(TypeError, options.IntegerOption, self.data.LONG,
                      self.data.SHORT, 'a', self.data.DESCRIPTION)

  def testBadIntegerValue(self):
    """Verifies a bad Integer value fails properly."""
    self.assertRaises(TypeError, self.option.SetValue, self.data.DESCRIPTION)

  def testCommandDefaultArgs(self):
    """Verifies an empty command list is generated successfully."""
    self.assertEqual([], self.option.Command())
    self.assertEqual([], self.option.Command(short=True))

  def testCommandNonDefaultArgs(self):
    """Verifies command list with non-default arguments is generated."""
    self.option.SetValue(self.data.VALUE)
    self.assertEqual([self.data.LONG, str(self.data.VALUE)],
                     self.option.Command())
    self.assertEqual([self.data.SHORT, str(self.data.VALUE)],
                     self.option.Command(short=True))

  def testString(self):
    """Verifies the String conversion of IntegerOption is correct."""
    option_str = (
        "(Long: '%s', Short: '%s', Description: '%s', Default: %s, "
        'DataTypes: %s, Value: %s)' %
        (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
         self.data.DEFAULT, self.data.TYPE_INT_TYPES, self.data.DEFAULT))
    self.assertEqual(str(self.option), option_str)

  def testRepr(self):
    """Verifies the String representation of IntegerOption is correct."""
    option_repr = (
        "options.IntegerOption('%s', '%s', '%s', %s, %s, %s)" %
        (self.data.LONG, self.data.SHORT,
         self.data.DESCRIPTION, self.data.DEFAULT, self.data.TYPE_INT_TYPES,
         self.data.DEFAULT))
    self.assertEqual(repr(self.option), option_repr)


class TestStringOptionClass(unittest.TestCase):
  """Verifies the StringOption class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.StringOption(self.data.LONG, self.data.SHORT,
                                       self.data.DESCRIPTION,
                                       self.data.STRING_DEFAULT)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testValidUnicodeString(self):
    """Verifies unicode strings work properly."""
    default = u'option'
    self.option.SetValue(default)
    self.assertEqual(self.option.value, default)

  def testBadStringDefaultOption(self):
    """Verifies a bad String default works properly."""
    self.assertRaises(TypeError, options.StringOption, self.data.LONG,
                      self.data.SHORT, self.data.DESCRIPTION, self.data.DEFAULT)

  def testBadStringValue(self):
    """Verifies a bad String value fails properly."""
    self.assertRaises(TypeError, self.option.SetValue, self.data.DEFAULT)

  def testCommandDefaultArgs(self):
    """Verifies an empty command list is generated successfully."""
    self.assertEqual([], self.option.Command())
    self.assertEqual([], self.option.Command(short=True))

  def testCommandNonDefaultArgs(self):
    """Verifies command list with non-default arguments is generated."""
    self.option.SetValue('b')
    self.assertEqual([self.data.LONG, '"b"'], self.option.Command())
    self.assertEqual([self.data.SHORT, '"b"'], self.option.Command(short=True))

  def testString(self):
    """Verifies the String conversion of StringOption is correct."""
    option_str = (
        "(Long: '%s', Short: '%s', Description: '%s', Default: '%s', "
        "DataTypes: %s, Value: '%s')" %
        (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
         self.data.STRING_DEFAULT, self.data.TYPE_STRING_TYPES,
         self.data.STRING_DEFAULT))
    self.assertEqual(str(self.option), option_str)

  def testRepr(self):
    """Verifies the String representation of StringOption is correct."""
    option_repr = (
        "options.StringOption('%s', '%s', '%s', '%s', %s, '%s')" %
        (self.data.LONG, self.data.SHORT,
         self.data.DESCRIPTION, self.data.STRING_DEFAULT,
         self.data.TYPE_STRING_TYPES, self.data.STRING_DEFAULT))
    self.assertEqual(repr(self.option), option_repr)


class TestFloatOptionClass(unittest.TestCase):
  """Verifies the FloatOption class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.FloatOption(self.data.LONG, self.data.SHORT,
                                      self.data.DESCRIPTION,
                                      self.data.FLOAT_DEFAULT)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testBadFloatDefaultOption(self):
    """Verifies a bad Float default works properly."""
    self.assertRaises(TypeError, options.FloatOption, self.data.LONG,
                      self.data.SHORT, 'a', self.data.DESCRIPTION)

  def testBadSetValue(self):
    """Verifies a bad Float value fails properly."""
    self.assertRaises(TypeError, self.option.SetValue, self.data.DESCRIPTION)

  def testCommandDefaultArgs(self):
    """Verifies an empty command list is generated successfully."""
    self.assertEqual([], self.option.Command())
    self.assertEqual([], self.option.Command(short=True))

  def testCommandNonDefaultArgs(self):
    """Verifies command list with non-default arguments is generated."""
    self.option.SetValue(1.1)
    self.assertEqual([self.data.LONG, str(1.1)], self.option.Command())
    self.assertEqual([self.data.SHORT, str(1.1)],
                     self.option.Command(short=True))

  def testString(self):
    """Verifies the String conversion of FloatOption is correct."""
    option_str = (
        "(Long: '%s', Short: '%s', Description: '%s', Default: %s, "
        'DataTypes: %s, Value: %s)' %
        (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
         self.data.FLOAT_DEFAULT, self.data.TYPE_FLOAT_TYPES,
         self.data.FLOAT_DEFAULT))
    self.assertEqual(str(self.option), option_str)

  def testRepr(self):
    """Verifies the String representation of FloatOption is correct."""
    option_repr = (
        "options.FloatOption('%s', '%s', '%s', %s, %s, %s)" %
        (self.data.LONG, self.data.SHORT,
         self.data.DESCRIPTION, self.data.FLOAT_DEFAULT,
         self.data.TYPE_FLOAT_TYPES, self.data.FLOAT_DEFAULT))
    self.assertEqual(repr(self.option), option_repr)


class TestSetOptionClass(unittest.TestCase):
  """Verifies the Set Option class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.SetOption(self.data.LONG, self.data.SHORT,
                                    self.data.DESCRIPTION, self.data.SET_LIST,
                                    self.data.SET_DEFAULT)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testBadSetDefaultOption(self):
    """Verifies a bad Set default works properly."""
    self.assertRaises(TypeError, options.SetOption, self.data.LONG,
                      self.data.SHORT, self.data.DEFAULT, self.data.DESCRIPTION,
                      self.data.DESCRIPTION)

  def testBadSetValue(self):
    """Verifies a bad Set value fails properly."""
    self.assertRaises(TypeError, self.option.SetValue, self.data.DEFAULT)

  def testCommandDefaultArgs(self):
    """Verifies an empty command list is generated successfully."""
    self.assertEqual([], self.option.Command())
    self.assertEqual([], self.option.Command(short=True))

  def testCommandNonDefaultArgs(self):
    """Verifies command list with non-default arguments is generated."""
    self.option.SetValue('acc')
    self.assertEqual([self.data.LONG, '"acc"'], self.option.Command())
    self.assertEqual([self.data.SHORT, '"acc"'],
                     self.option.Command(short=True))

  def testString(self):
    """Verifies the String conversion of SetOption is correct."""
    option_str = ("(Long: '%s', Short: '%s', Description: '%s', Set: %s, "
                  "Default: '%s', Value: '%s')" %
                  (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
                   self.data.SET_LIST, self.data.SET_DEFAULT,
                   self.data.SET_DEFAULT))
    self.assertEqual(str(self.option), option_str)

  def testRepr(self):
    """Verifies the String representation of SetOption is correct."""
    option_repr = (
        "options.SetOption('%s', '%s', '%s', %s, '%s', '%s')" %
        (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
         self.data.SET_LIST, self.data.SET_DEFAULT, self.data.SET_DEFAULT))
    self.assertEqual(repr(self.option), option_repr)


class TestRangeOptionClass(unittest.TestCase):
  """Verifies the Range Option class works properly."""

  def setUp(self):
    options.ENABLED_COMMAND_QUOTES = True
    self.data = OptionTestData
    self.option = options.RangeOption(self.data.LONG, self.data.SHORT,
                                      self.data.DESCRIPTION, self.data.LOW,
                                      self.data.HIGH, self.data.DEFAULT)

  def tearDown(self):
    options.ENABLED_COMMAND_QUOTES = False

  def testBadRangeDefaultOption(self):
    """Verifies a bad Range default works properly."""
    self.assertRaises(TypeError, options.RangeOption, self.data.LONG,
                      self.data.SHORT, self.data.DEFAULT, self.data.DESCRIPTION,
                      self.data.DESCRIPTION, self.data.HIGH)

  def testBadSetValue(self):
    """Verifies a bad Range value fails properly."""
    self.assertRaises(TypeError, self.option.SetValue, self.data.DESCRIPTION)
    self.assertRaises(ValueError, self.option.SetValue, 11)

  def testCommandDefaultArgs(self):
    """Verifies an empty command list is generated successfully."""
    self.assertEqual([], self.option.Command())
    self.assertEqual([], self.option.Command(short=True))

  def testCommandNonDefaultArgs(self):
    """Verifies command list with non-default arguments is generated."""
    self.option.SetValue(self.data.VALUE)
    self.assertEqual([self.data.LONG, str(self.data.VALUE)],
                     self.option.Command())
    self.assertEqual([self.data.SHORT, str(self.data.VALUE)],
                     self.option.Command(short=True))

  def testString(self):
    """Verifies the String conversion of RangeOption is correct."""
    option_str = ("(Long: '%s', Short: '%s', Description: '%s', Low: %s, "
                  'High: %s, Default: %s, Value: %s)' %
                  (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
                   self.data.LOW, self.data.HIGH, self.data.DEFAULT,
                   self.data.DEFAULT))
    self.assertEqual(str(self.option), option_str)

  def testRepr(self):
    """Verifies the String representation of RangeOption is correct."""
    option_repr = (
        "options.RangeOption('%s', '%s', '%s', %s, %s, %s, %s)" %
        (self.data.LONG, self.data.SHORT, self.data.DESCRIPTION,
         self.data.LOW, self.data.HIGH, self.data.DEFAULT, self.data.DEFAULT))
    self.assertEqual(repr(self.option), option_repr)


class TestNoQuoteOptions(unittest.TestCase):
  """Verifies the option.ENABLED_COMMAND_QUOTES works properly."""

  def setUp(self):
    self.data = OptionTestData
    self.option = options.SetOption(self.data.LONG, self.data.SHORT,
                                    self.data.DESCRIPTION, self.data.SET_LIST,
                                    self.data.SET_DEFAULT)

  def testCommandQuotes(self):
    """Verifies command list with non-default arguments is generated."""
    options.ENABLED_COMMAND_QUOTES = True
    self.option.SetValue('acc')
    self.assertEqual([self.data.LONG, '"acc"'], self.option.Command())
    self.assertEqual([self.data.SHORT, '"acc"'],
                     self.option.Command(short=True))

  def testCommandNoQuotes(self):
    """Verifies command list with non-default arguments is generated."""
    options.ENABLED_COMMAND_QUOTES = False
    self.option.SetValue('acc')
    self.assertEqual([self.data.LONG, 'acc'], self.option.Command())
    self.assertEqual([self.data.SHORT, 'acc'],
                     self.option.Command(short=True))


if __name__ == '__main__':
  unittest.main()
