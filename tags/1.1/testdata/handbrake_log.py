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
"""Handbrake log data for testing."""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'


import os


class ChapterLineTestData(object):
  """Test data for chapter line from Handbrake."""
  LINE = '    + 1: cells 0->2, 48235 blocks, duration 00:02:13'
  BAD_LINE = '    + 1, English (AC3) (Dolby Surround), 48000Hz, 192000bps'
  NUMBER = 1
  START = 0
  END = 2
  BLOCKS = 48235
  DURATION = '00:02:13'


class AudioLineTestData(object):
  """Test data for audio line from Handbrake."""
  LINE = '    + 1, English (AC3) (Dolby Surround), 48000Hz, 192000bps'
  LINE_TWO = ("    + 1, English (AC3) (Director's Commentary) (2.0 ch), "
              '48000Hz, 192000bps')
  BAD_LINE = '    + 1: cells 0->2, 48235 blocks, duration 00:02:13'
  NUMBER = 1
  ENCODER = 'AC3'
  SAMPLE_RATE = 48000
  BIT_RATE = 192000
  FORMAT = 'Dolby Surround'
  FORMAT_TWO = '2.0 ch'
  LANGUAGE = 'English'


class SubtitleLineTestData(object):
  """Test data for subtitle line from Handbrake."""
  LINE = '    + 1, English (Closed Caption) (iso639-2: eng)'
  LINE_TWO = '    + 1, English (iso639-2: eng)'
  BAD_LINE = '    + 1, English (AC3) (Dolby Surround), 48000Hz, 192000bps'
  LANGUAGE = 'English'
  ISO_CODE = 'iso639-2'
  ISO_LANGUAGE = 'eng'
  NUMBER = 1


class TitleSectionTestData(object):
  """Test data for verifying dvd.Dvd._ProcessTitleSection."""
  CHAPTER_LOG = [ChapterLineTestData.LINE]
  CHAPTER_ARGS = (0, 2, 48235, '00:02:13', 1)
  AUDIO_LOG = [AudioLineTestData.LINE]
  AUDIO_ARGS = ('AC3', 'Dolby Surround', 48000, 192000, 'English', 1)
  SUBTITLE_LOG = [SubtitleLineTestData.LINE]
  SUBTITLE_ARGS = ('English', 'iso639-2', 'eng', 1)


class ParseVideoTileSetLineTestData(object):
  """Test data for verifying dvd.Dvd._ParseVideoTileSetTestData."""
  LINE = '  + vts 1, ttn 1, cells 0->24 (1939167 blocks)'
  TILE = 1
  NUMBER = 1
  START = 0
  END = 24
  BLOCKS = 1939167


class ParseDurationLineTestData(object):
  """Test data for verifying dvd.Dvd._ParseDurationLine."""
  LINE = '  + duration: 01:26:38'
  DURATION = '01:26:38'


class ParseSizeLineTestData(object):
  """Test data for verifying dvd.Dvd._ParseSizeLine."""
  LINE = '  + size: 720x480, aspect: 1.78, 23.976 fps'
  HORIZONTAL_SIZE = 720
  VERTICAL_SIZE = 480
  ASPECT = 1.78
  FRAME_RATE = 23.976


class ParseAutocropLineTestData(object):
  """Test data for verifying dvd.Dvd._ParseAutocropLine."""
  LINE = '  + autocrop: 1/2/3/4'
  TOP = 1
  BOTTOM = 2
  LEFT = 3
  RIGHT = 4


class ExtractTitleFromLogTestData(object):
  """Test data for verifying dvd.Dvd._ExtractTitleFromLog."""
  INDEXES = [6, 28, 33]
  TITLE_ARGS = (1, 1, 0, 24, 1939167, '01:26:38', 720, 480, 1.78, 23.976, 0,
                0, 0, 0, False, [], [], [], False)

  def __init__(self):
    f = open('./testdata/handbrake_dvd_logs/handbrake_title.log')
    # Strips newline characters and stores each line as a String in a List.
    self.log_raw = f.readlines()
    f.close()
    self.log = ''.join(self.log_raw).splitlines()


class IndexHandbrakeLogTestData(object):
  """Test data for verifying dvd.Dvd._IndexHandbrakeLog."""
  TITLES = [9, 46, 75, 103]
  NAME = 'FIREFLY_D1'
  DVD_SIGNATURE = [(21, 4, 4), (13, 4, 4), (13, 3, 4), (2, 1, 0)]

  def __init__(self):
    f = open('./testdata/handbrake_dvd_logs/handbrake_log_index_test.log')
    # Strips newline characters and stores each line as a String in a List.
    self.log_raw = f.readlines()
    f.close()
    self.log = ''.join(self.log_raw).splitlines()


class IntegrationTest(object):
  """Test data for integration testing mulitple DVD's."""

  def __init__(self):
    self.files = os.listdir('./testdata/handbrake_dvd_logs/')
    self.files.pop(self.files.index('.svn'))
    for index in xrange(len(self.files)):
      self.files[index] = './testdata/handbrake_dvd_logs/' + self.files[index]
