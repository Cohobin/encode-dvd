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
"""Generic Option classes for handling command line option interactions.

Attributes:
  ENABLE_COMMAND_QUOTES: Boolean True to enable quoting of String/Unicode values
    returned by Command().  False disables quoting.  Command() will always
    return a String; default allows for easy consumption with subprocess.
    Default False.
"""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'
__version__ = '1.0'

import types


ENABLED_COMMAND_QUOTES = False


class Option(object):
  """Abstract base option class.

  Attributes:
    long: String commandline long option argument.
    short: String commandline short option argument.
    default: Data option default value for argument.
    description: String extended description of option.
    value: Data option value for arugment.
    _valid_datatypes: List containing valid datatypes for this option.
  """

  def __init__(self, long, short, description, default=None,
               datatypes=None, value=None):
    """Initalize option class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      default: Data option default value for argument.  Default None.
      datatypes: Datatype or List containing valid datatypes for this option.
      value: Data option value for argument, Default default.
    """
    self.long = long
    self.short = short
    self.default = default
    self.description = description
    self._valid_types = []
    if not isinstance(datatypes, list):
      self._valid_types.append(type(datatypes))
    else:
      for datatype in datatypes:
        self._valid_types.append(type(datatype))
    if not value:
      self.SetValue(default)
    else:
      self.SetValue(value)

  def SetValue(self, value):
    """Sets value of option, enforcing restrictions if needed.

    Args:
      value: Data option value for argument to set.

    Raises:
      TypeError: If the value is of the incorrect datatype.
    """
    if self._CheckType(value):
      self.value = value
    else:
      raise TypeError('Option value (%s) is not an allowed DataTypes! (%s)' %
                      (value, self._valid_types))
    self.value = value

  def Command(self, short=False):
    """Generates formatted command line arguments for this argument.

    Args:
      short: Boolean True to return a list using the short arguments.  Default
        long arguments.

    Returns:
      List containing the formatted command line arguments.  If the option
      specified is the default value, no arguments are returned.
    """
    quoted_value = self._QuoteAttributes([self.value], single=False)[0]
    results = [None, quoted_value]
    if short:
      results[0] = self.short
    else:
      results[0] = self.long
    if self.value == self.default or self.value is None:
      results = []
    return results

  def _CheckType(self, value):
    """Verifies a given value is one of the given datatypes.

    isinstance cannot check for NoneType datadatatypes, so this is needed.

    Args:
      value: data to verify datatype.

    Returns:
      Boolean True if value is of given datatype, False otherwise.
    """
    results = False
    value_type = type(value)
    for datatype in self._valid_types:
      if value_type == datatype:
        results = True
        break
    return results

  def _QuoteAttributes(self, attributes, single=True):
    """Quotes required attributes.

    An attribute requiring quotes is a String or Unicode attribute.  All other
    attributes are typecast to String for use in __str__ and __repr__.

    Args:
      attributes: List of attributes that may require quoting.
      single: Boolean True to wrap in single quotes, False for double quotes.

    Returns:
      List of String attributes, ones requiring quoting (String, Unicode)
      wrapped in quotes.  Results guaranteed to be in the same order.
    """
    results = []
    for attribute in attributes:
      if isinstance(attribute, types.StringTypes) and ENABLED_COMMAND_QUOTES:
        if single:
          results.append("'%s'" % attribute)
        else:
          results.append('"%s"' % attribute)
      else:
        results.append(str(attribute))
    return results

  def __str__(self):
    """Returns the String of this object."""
    results = []
    attributes = self._QuoteAttributes(
        [self.long, self.short, self.description,
         self.default, self._valid_types, self.value])
    options = ['Long: ', ', Short: ', ', Description: ', ', Default: ',
               ', DataTypes: ', ', Value: ']
    for option in zip(options, attributes):
      results.extend([option[0], option[1]])
    return '(%s)' % ''.join(results)

  def __repr__(self):
    """Returns the String representation of this object."""
    attributes = self._QuoteAttributes(
        [self.long, self.short, self.description,
         self.default, self._valid_types, self.value])
    return 'options.%s(%s)' % (self.__class__.__name__, ', '.join(attributes))


class AllTypesOption(Option):
  """Abstract base option class that handles all primitive datatypes."""

  def __init__(
      self, long, short, description, default=None,
      datatypes=[None, int(), float(), str(), unicode(), bool(), long()],
      value=None):
    """Initalize AllTypesOption class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      default: Data option default value for argument.  Default None.
      datatypes: Datatype or List containing valid datatypes for this option.
        Default all primative Python datatypes.
      value: Data option value for argument.
    """
    Option.__init__(self, long, short, description, default, datatypes, value)


class BooleanOption(Option):
  """Boolean option.

  A Boolean option is a commandline option that only requires the flag to be
  present, with no additional qualifiers after it.
  """

  def __init__(self, long, short, description, default=None,
               datatypes=[bool(), None], value=None):
    """Initalize BooleanOption class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      default: Boolean option default value for argument.  Default None.
      datatypes: Datatype or List containing valid datatypes for this option.
        Default Boolean and None.
      value: Data option value for argument, Default default.
    """
    Option.__init__(self, long, short, description, default, datatypes, value)

  def Command(self, short=False):
    """Generates formatted command line arguments for this argument.

    Args:
      short: Boolean True to return a list using the short arguments.  Default
        long arguments.

    Returns:
      List containing only the argument if value is True, otherwise an empty
      List.
    """
    results = []
    if self.value:
      if short:
        results.append(self.short)
      else:
        results.append(self.long)
    return results


class IntegerOption(Option):
  """Integer Option.

  A Integer Option is an commandline option that only requires a single integer
  after the argument.
  """

  def __init__(self, long, short, description, default=None,
               datatypes=[int(), None], value=None):
    """Initalize IntegerOption class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      default: Integer option default value for argument.  Default None.
      datatypes: Datatype or List containing valid datatypes for this option.
        Default Integer and None.
      value: Integer option value for argument.
    """
    Option.__init__(self, long, short, description, default, datatypes, value)


class StringOption(Option):
  """String Option.

  A String Option is a commandline option that only requires a single string
  after the arguement. The string will be wrapped in double quotes if
  options.ENABLED_COMMAND_QUOTES is True.
  """

  def __init__(self, long, short, description, default=None,
               datatypes=[str(), unicode(), None], value=None):
    """Initalize StringOption class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      default: String option default value for argument.  Default None.
      datatypes: Datatype or List containing valid datatypes for this option.
        Default String, Unicode and None.
      value: Integer option value for argument.
    """
    Option.__init__(self, long, short, description, default, datatypes, value)


class FloatOption(Option):
  """Float Option.

  A Float Option is a commandline option that only requires a float number
  after the arguement.
  """

  def __init__(self, long, short, description, default=None,
               datatypes=[float(), None], value=None):
    """Initalize FloatOption class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      default: Float option default value for argument.  Default None.
      datatypes: Datatype or List containing valid datatypes for this option.
        Default Float and None.
      value: Float option value for argument.
    """
    Option.__init__(self, long, short, description, default, datatypes, value)


class SetOption(AllTypesOption):
  """Set Option.

  A Set Option is a commandline option which requires a given arguement option
  to be a valid member of a given set.  This is most commonly used for options
  that have a number of valid string values, etc.
  """

  def __init__(self, long, short, description, set, default=None, value=None):
    """Initalize SetOption class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      set: List containing the valid set of data for this option.
      default: Data option default value for argument.  Default None.
      value: Data option value for argument.
    """
    if not isinstance(set, list):
      raise TypeError('SetOption set is not a List! %s' % set)
    self.set = set
    self.SetValue(value)
    Option.__init__(self, long, short, description, default)

  def SetValue(self, value):
    """Sets value of option, enforcing restrictions if needed.

    Args:
      value: Data option value for argument to set, must be in self.set.
    """
    if value in self.set or value is None:
      self.value = value
    else:
      raise TypeError('SetOption value is not in Set! %s' % value)

  def __str__(self):
    """Returns the String of this object."""
    results = []
    attributes = self._QuoteAttributes(
        [self.long, self.short, self.description,
         self.set, self.default, self.value])
    options = ['Long: ', ', Short: ', ', Description: ', ', Set: ',
               ', Default: ', ', Value: ']
    for option in zip(options, attributes):
      results.extend([option[0], option[1]])
    return '(%s)' % ''.join(results)

  def __repr__(self):
    """Returns the String representation of this object."""
    attributes = self._QuoteAttributes(
        [self.long, self.short, self.description,
         self.set, self.default, self.value])
    return 'options.SetOption(%s)' % ', '.join(attributes)


class RangeOption(AllTypesOption):
  """Range Option.

  A Range Option is a commandline option that accepts a given arguement option
  to be a piece of data between two given points.  The data can be of anytype,
  as long as it can be correctly compared to other data of the same type.
  """

  def __init__(self, long, short, description,
               low, high, default=None, value=None):
    """Initalize RangeOption class.

    Args:
      long: String commandline long option argument.
      short: String commandline short option argument.
      description: String extended description of option.
      low: Data lowest value accepted for this arguement.  Inclusive.
      high: Data highest value accepted for this arguement.  Inclusive.
      default: Data option default value for argument.  Default None.
      value: Data option value for argument.
    """
    if type(low) != type(high):
      raise TypeError('RangeOption range values must be of the same type! '
                      '%s, %s' % (low, high))
    self.low = low
    self.high = high
    self.SetValue(value)
    Option.__init__(self, long, short, description, default)

  def SetValue(self, value):
    """Sets value of option, enforcing restrictions if needed.

    Args:
      value: Data option value for argument to set, must be same datatype as
        self.low or self.high; and be between them inclusively.

    Raises:
      TypeError: If the datatype of the value does not match the range min/max.
      ValueError: If the value is outside the range of min and max.
    """
    if type(value) != type(self.low) and value is not None:
      raise TypeError('RangeOption value (%s%s) is not the same datatype! %s' %
                      (value, type(value), type(self.low)))
    elif value >= self.low and value <= self.high or value is None:
      self.value = value
    else:
      raise ValueError('RangeOption value is not in range! %s (%s-%s)' %
                       (value, self.low, self.high))

  def __str__(self):
    """Returns the String of this object."""
    results = []
    attributes = self._QuoteAttributes(
        [self.long, self.short, self.description,
         self.low, self.high, self.default, self.value])
    options = ['Long: ', ', Short: ', ', Description: ', ', Low: ', ', High: ',
               ', Default: ', ', Value: ']
    for option in zip(options, attributes):
      results.extend([option[0], option[1]])
    return '(%s)' % ''.join(results)

  def __repr__(self):
    """Returns the String representation of this object."""
    attributes = self._QuoteAttributes(
        [self.long, self.short, self.description, self.low, self.high,
         self.default, self.value])
    return 'options.RangeOption(%s)' % ', '.join(attributes)
