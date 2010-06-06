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
"""Sane absolute path module.

Generates sane absolute paths, instead of os.path.abspath.
"""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'
__version__ = '1.0'

import os


def AbsPath(path):
  """Standardizes a given path to an absolute path.

  Ensures the returned path is an absolute path, expanding user home
  direcotories (~), and ensures that directories have a trailing separator.

  Args:
    path: String path for file or directory.

  Returns:
    A string containing the full path to the file or directory.  If directory,
    it will ensure a trailing separator.
  """
  path = os.path.abspath(os.path.expanduser(path))
  if os.path.isdir(path):
    if not path.endswith(os.sep):
      path = ''.join([path, os.sep])
  return path
