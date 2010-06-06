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
"""Test suite for abs_path.

This test suite requires the use of the mox module for python.  This is located
here: http://code.google.com/p/pymox/wiki/MoxDocumentation.
"""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'

import os
import unittest
import abs_path


try:
  import mox
except ImportError:
  raise ImportError('Python MOX must be installed to run this unittest.  See: '
                    'http://code.google.com/p/pymox/wiki/MoxDocumentation for '
                    'information on how to install this framework.')


class TestAbsPath(unittest.TestCase):
  """Verifies the basic methods in abs_path work properly."""

  def setUp(self):
    self.mox = mox.Mox()
    self.real_os_path = abs_path.os.path
    abs_path.os.path = self.mox.CreateMock(os.path)

  def tearDown(self):
    self.mox.UnsetStubs()
    abs_path.os.path = self.real_os_path

  def testAbsPathFile(self):
    """Verifies AbsPath works properly for a file."""
    abs_path.os.path.expanduser('file').AndReturn('file')
    abs_path.os.path.abspath('file').AndReturn('file')
    abs_path.os.path.isdir('file').AndReturn(False)
    self.mox.ReplayAll()
    self.assertEqual(abs_path.AbsPath('file'), 'file')

  def testAbsPathDirectory(self):
    """Verifies AbsPath works properly for a directory."""
    abs_path.os.path.expanduser('file').AndReturn('file')
    abs_path.os.path.abspath('file').AndReturn('file')
    abs_path.os.path.isdir('file').AndReturn(True)
    self.mox.ReplayAll()
    self.assertEqual(abs_path.AbsPath('file'), 'file/')


if __name__ == '__main__':
  unittest.main()
