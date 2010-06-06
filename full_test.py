#!/usr/bin/python2.6
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
"""Test suite for encode_dvd."""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'

import optparse
import sys
import unittest
import abs_path_test
import dvd_test
import encode_dvd_test
import handbrake_options_test
import handbrake_test
import options_test

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-v', '--verbosity', action='store', type='int',
                    dest='verbosity', default=1, help='how verbose the output '
                    'should be.  0=none, 3=most; default=1')
  options = parser.parse_args()[0]
  if not isinstance(options.verbosity, int):
    options.verbosity = 1

  suite = unittest.TestSuite()
  suite.addTest(unittest.findTestCases(dvd_test))
  suite.addTest(unittest.findTestCases(options_test))
  suite.addTest(unittest.findTestCases(handbrake_options_test))
  suite.addTest(unittest.findTestCases(handbrake_test))
  suite.addTest(unittest.findTestCases(encode_dvd_test))
  suite.addTest(unittest.findTestCases(abs_path_test))
  print '%s\nRunning %s tests...\n%s' % ('_' * 80,
                                         suite.countTestCases(),
                                         '=' * 80)
  results = unittest.TextTestRunner(verbosity=options.verbosity).run(suite)
  if not results.wasSuccessful():
    print 'FAIL'
    sys.exit(1)
