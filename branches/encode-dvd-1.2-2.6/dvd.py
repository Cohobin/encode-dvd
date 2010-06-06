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
"""DVD Python module that holds DVD information in an object."""

import datetime
import os


class Error(Exception):
  """Generic dvd module Exception."""


class InvalidDuration(Error):
  """An invalid duration was specified."""


class AudioFormatUnknown(Error):
  """An audio mixdown format could not be determined."""


class InvalidHandbrakeLogLine(Error):
  """A Handbrake Log Line format is not what is expected."""


class TitleNotFoundError(Error):
  """If a given title number is not within a DVD object."""


class BaseDvdObject(object):
  """Base object used for DVD objects."""

  def CreateDuration(self, duration):
    """Creates a valid datetime.datetime object from a duration representation.

    A duration repsentation is a String in the format HH:MM:SS or a
    datetime.datetime object.

    Args:
      duration: Datetime/String objects duration.

    Raises:
      InvalidDuration: If duration is not valid.

    Returns:
      datetime.datetime object containing the duration of the chapter.
    """
    if isinstance(duration, datetime.datetime):
      results = duration
    elif isinstance(duration, str):
      try:
        hours, minutes, seconds = map(lambda x: int(x), duration.split(':'))
        results = datetime.datetime(1, 1, 1, hours, minutes, seconds)
      except (TypeError, ValueError):
        raise InvalidDuration('Duration String format incorrect expected: '
                              'HH:MM:SS, received: %s' % duration)
    else:
      raise InvalidDuration('Duration must be String or datetime.time object.')
    return results

  def GetDuration(self):
    """Returns the duration of the object as a String, or a default duration."""
    duration = getattr(self, 'duration', datetime.datetime(1, 1, 1, 0, 0, 0))
    return str(duration.time())


class Chapter(BaseDvdObject):
  """Information for a single chapter on a DVD.

  Attributes:
    cell_start: Integer cell start for title.  Default 0.
    cell_end: Integer cell end for title.  Default 0.
    cell_blocks: Integer number of DVD data blocks cells' use for this title.
    duration: Datetime.time object that contains the total playback duration for
      this title.  Duration is specified in 24-hour format: HH:MM:SS.
    number: Integer chapter number for this chapter.  Default 0.
    strict: Boolean True to enforce strict value checking.  Default False.
  """

  def __init__(self, start=0, end=0, blocks=0,
               duration='00:00:00', number=1, strict=False):
    """Initalize chapter data.

    Args:
      start: Integer cell start number.  Default 0.
      end: Integer cell end number.  Default 0.
      blocks: Integer number of data blocks used on DVD.  Default 0.
      duration: Datetime/String duration of chapter length in HH:MM:SS format.
        Default 00:00:00.
      number: Integer this chapter's number.  Default 1.
      strict: Boolean True to enforce strict value checking.  Default False.

    Raises:
      TypeError: If arguments passed to Chapter are not valid.
      ValueError: If argument values are not valid.
    """
    self._ValidateOptions(start, end, blocks, duration, number, strict)
    self.start = start
    self.end = end
    self.blocks = blocks
    self.duration = self.CreateDuration(duration)
    self.number = number
    self.strict = strict

  def __cmp__(self, other):
    """Comparator for use with sorting.

    All DVD objects are compared with the index number for that particular type.

    Args:
      other: Chapter object or Integer to be compared to.

    Returns:
      Integer 1 this object is greater, 0 objects are equal, -1 other object is
      greater.
    """
    if isinstance(other, Chapter):
      return cmp(self.number, other.number)
    else:
      return cmp(self.number, other)

  def __str__(self):
    """Returns the String of this object."""
    return (
        'number: %s, start: %s, end: %s, blocks: %s, duration: %s' %
        (self.number, self.start, self.end, self.blocks, self.GetDuration()))

  def __repr__(self):
    """Returns the String representation of this object."""
    return ('dvd.Chapter(start=%s, end=%s, blocks=%s, '
            "duration='%s', number=%s, strict=%s)" %
            (self.start, self.end, self.blocks,
             self.GetDuration(), self.number, self.strict))

  def _ValidateOptions(self, start, end, blocks, duration, number, strict):
    """Validates Chapter class options.

    Args:
      start: Integer cell start number.  Default 0.
      end: Integer cell end number.  Default 0.
      blocks: Integer number of data blocks used on DVD.  Default 0.
      duration: Datetime/String duration of chapter length in HH:MM:SS format.
        Default 00:00:00.
      number: Integer this chapter's number.  Default 1.
      strict: Boolean True to enforce strict value checking.  Default False.

    Raises:
      TypeError: If arguments passed are not valid.
      ValueError: If argument values are not valid.
    """
    if (not isinstance(start, int) or
        not isinstance(end, int) or
        not isinstance(blocks, int) or
        not isinstance(number, int)):
      raise TypeError('Expected Integer arguements: start(%s), end(%s),'
                      'blocks(%s), number(%s)' %
                      (start, end, blocks, number))
    if start < 0 or end < 0 or number < 0:
      raise ValueError('Integer arguements must be positive or 0.')
    self.CreateDuration(duration)
    if strict and start > end:
      raise ValueError('Cell start must start before cell end.')
    if strict and blocks < 0:
      raise ValueError('Cell blocks must be positive or 0.')

  def _ProcessLine(self, line):
    """Processes a handbrake log line for chapter options.

    A chapter line in the Handbrake log looks like the following:
        + 1: cells 0->0, 48235 blocks, duration 00:02:13

    Args:
      line: String containing a chapter line from handbrake.

    Raises:
      InvalidHandbrakeLogLine: If log line is not in the expected format.

    Returns:
      Tuple containing (<int> start, <int> end, <int> blocks, <str> duration,
      <int> number).
    """
    try:
      cells, blocks, duration = line.split(',')
      number, cells = cells.split(':')
      blocks = int(blocks.split()[0])
      duration = duration.split()[-1]
      number = int(number.split('+')[-1])
      start, end = map(lambda x: int(x), cells.split()[-1].split('->'))
    except ValueError, error:
      raise InvalidHandbrakeLogLine('ProcessLine failure: %s, %s' %
                                    (error, line))
    return (start, end, blocks, duration, number)

  def ParseHandbrakeLine(self, line):
    """Parses a title's chapter line from Handbrake, and sets attributes.

    This will parse a Handbrake chapter line, and set this chapter object to the
    values determined from the line.

    A chapter line in the Handbrake log looks like the following:
        + 1: cells 0->0, 48235 blocks, duration 00:02:13

    Args:
      line: String containing a chapter line from Handbrake.

    Raises:
      InvalidHandbrakeLogLine: If log line is not in the expected format.
    """
    start, end, blocks, duration, number = self._ProcessLine(line)
    try:
      self._ValidateOptions(start, end, blocks, duration, number, self.strict)
    except (TypeError, ValueError), error:
      raise InvalidHandbrakeLogLine(
          'Chapter log line not parsed correctly: %s, line: %s' % (error, line))
    self.start = start
    self.end = end
    self.blocks = blocks
    self.duration = self.CreateDuration(duration)
    self.number = number


class Audio(object):
  """Information for an Audio track on a DVD.

  Attributes:
    encoder: String audio encoder used to record track.  Default 'AC3'.
    format: String surround sound format.  Default '2.0 ch'.
    sample_rate: Integer number of samples per second (Hz).  Default 48000.
    bit_rate: Integer number of bits used to encode stream (bps).
      Default 192000.
    language: String audio track language.  Default 'English'.
    number: Integer audio track number.  Default 1.
    strict: Boolean True to enforce strict checking.  Default False.
  """

  def __init__(self, encoder='AC3', format='2.0 ch', sample_rate=48000,
               bit_rate=192000, language='English', number=1, strict=False):
    """Initalize audio data.

    Args:
      encoder: String encoder used for autio track.Default 'AC3'.
      format: String surround sound format.  Default '2.0 ch'.
      sample_rate: Integer number of samples per second (Hz).  Default 48000.
      bit_rate: Integer number of bits used to encode stream (bps).
        Default 192000.
      language: String audio track language.  Default 'English'.
      number: Integer audio track number.  Default 1.
      strict: Boolean True to enforce strict value checking.  Default False.

    Raises:
      TypeError: If arguments passed to Chapter are not valid.
    """
    self._ValidateOptions(encoder, format, sample_rate,
                          bit_rate, language, number, strict)
    self.encoder = encoder.strip()
    self.format = format.strip()
    self.sample_rate = sample_rate
    self.bit_rate = bit_rate
    self.language = language.strip()
    self.number = number
    self.strict = strict

  def __cmp__(self, other):
    """Comparator for use with sorting.

    All DVD objects are compared with the index number for that particular type.

    Args:
      other: Audio object or Integer to be compared to.

    Returns:
      Integer 1 this object is greater, 0 objects are equal, -1 other object is
      greater.
    """
    if isinstance(other, Audio):
      return cmp(self.number, other.number)
    else:
      return cmp(self.number, other)

  def __str__(self):
    """Returns the String of this object."""
    return (
        'number: %s, encoder: %s, format: %s, '
        'sample rate: %s, bit rate: %s, language: %s' %
        (self.number, self.encoder, self.format, self.sample_rate,
         self.bit_rate, self.language))

  def __repr__(self):
    """Returns the String representation of this object."""
    return (
        "dvd.Audio(encoder='%s', format='%s', sample_rate=%s, "
        "bit_rate=%s, language='%s', number=%s, strict=%s)" %
        (self.encoder, self.format, self.sample_rate, self.bit_rate,
         self.language, self.number, self.strict))

  def _ValidateOptions(self, encoder, format, sample_rate, bit_rate,
                       language, number, strict):
    """Validates Audio class options.

    Args:
      encoder: String encoder used for autio track.Default 'AC3'.
      format: String surround sound format.  Default '2.0 ch'.
      sample_rate: Integer number of samples per second (Hz).  Default 48000.
      bit_rate: Integer number of bits used to encode stream (bps).
        Default 192000.
      language: String audio track language.  Default 'English'.
      number: Integer audio track number.  Default 1.
      strict: Boolean True to enforce strict value checking.  Default False.

    Raises:
      TypeError: If arguments passed are not valid.
      ValueError: If argument values are not valid.
    """
    if (not isinstance(encoder, str) or
        not isinstance(format, str) or
        not isinstance(language, str)):
      raise TypeError('Expected String arguements: encoder(%s), '
                      'format(%s), language(%s)' %
                      (encoder, format, language))
    if (not isinstance(sample_rate, int) or
        not isinstance(bit_rate, int) or
        not isinstance(number, int)):
      raise TypeError('Expected Integer arguements: sample_rate(%s), '
                      'bit_rate(%s), number(%s)' %
                      (sample_rate, bit_rate, number))
    if strict and number < 0:
      raise ValueError('Number must be positive or 0.')
    if strict and sample_rate < 0:
      raise ValueError('Sample Rate must be positive or 0.')
    if strict and bit_rate < 0:
      raise ValueError('Bit Rate must be positive or 0.')

  def _ProcessLine(self, line):
    """Processes a handbrake log line for audio options.

    A audio line in the Handbrake log looks like the following:
        + 1, English (AC3) (Dolby Surround), 48000Hz, 192000bps
        + 4, English (AC3) (Director's Commentary) (2.0 ch), 48000Hz, 192000bps

    Args:
      line: String containing an audio line from handbrake.

    Raises:
      InvalidHandbrakeLogLine: If log line is not in the expected format.

    Returns:
      Tuple containing (<str> encoder, <str> format, <int> sample_rate,
      <int> bit_rate, <int> number).
    """
    try:
      number, encoder, sample_rate, bit_rate = line.split(',')
      number = int(number.split('+')[-1])
      sample_rate = int(sample_rate.split('Hz')[0])
      bit_rate = int(bit_rate.split('bps')[0])
      language, encoder, format = encoder.split('(', 2)
      language = language.strip()
      encoder = encoder.split(')')[0].strip()
      format = format[format.rfind('(')+1:format.rindex(')')].strip()
    except ValueError, error:
      raise InvalidHandbrakeLogLine('ProcessLine failure: %s, %s' %
                                    (error, line))
    return (encoder, format, sample_rate, bit_rate, language, number)

  def ParseHandbrakeLine(self, line):
    """Parses a title's audio line from Handbrake, and sets attributes.

    This will parse a Handbrake audio line, and set this audio object to the
    values determined from the line.

    A audio line in the Handbrake log looks like the following:
        + 1, English (AC3) (Dolby Surround), 48000Hz, 192000bps
        + 4, English (AC3) (Director's Commentary) (2.0 ch), 48000Hz, 192000bps

    Args:
      line: String containing an audio line from handbrake.

    Raises:
      InvalidHandbrakeLogLine: If log line is not in the expected format.
    """
    encoder, format, sample_rate, bit_rate, language, number = (
        self._ProcessLine(line))
    try:
      self._ValidateOptions(encoder, format, sample_rate, bit_rate,
                            language, number, self.strict)
    except (TypeError, ValueError), error:
      raise InvalidHandbrakeLogLine(
          'Audio log line not parsed correctly: %s, line: %s' % (error, line))
    self.encoder = encoder.strip()
    self.format = format.strip()
    self.sample_rate = sample_rate
    self.bit_rate = bit_rate
    self.language = language.strip()
    self.number = number


class Subtitle(object):
  """Information for a subtitle track on a DVD.

  Attributes:
    language: String common language used for subtitles.  Default 'English'.
    iso_code: String ISO language abbreviation code identifier.
      Default 'iso639-2'.
      See http://www.loc.gov/standards/iso639-2/php/code_list.php
    iso_language: String iso-encoded language ID.  Default 'eng'.
    number: Integer subtitle track number.  Default 1.
    strict: Boolean True to enforce strict value checking.  Default False.
  """

  def __init__(self, language='English', iso_code='iso639-2',
               iso_language='eng', number=1, strict=False):
    """Initalize subtitle data.

    Args:
      language: String common language used for subtitles.  Default 'English'.
      iso_code: String ISO language abbreviation code identifier.
        Default 'iso639-2'.
        See http://www.loc.gov/standards/iso639-2/php/code_list.php
      iso_language: String iso-encoded language ID.  Default 'eng'.
      number: Integer subtitle track number.  Default 1.
      strict: Boolean True to enforce strict value checking.  Default False.

    Raises:
      TypeError: If arguments passed to Chapter are not valid.
    """
    self._ValidateOptions(language, iso_code, iso_language, number, strict)
    self.language = language.strip()
    self.iso_code = iso_code.strip()
    self.iso_language = iso_language.strip()
    self.number = number
    self.strict = strict

  def __cmp__(self, other):
    """Comparator for use with sorting.

    All DVD objects are compared with the index number for that particular type.

    Args:
      other: Subtitle object or Integer to be compared to.

    Returns:
      Integer 1 this object is greater, 0 objects are equal, -1 other object is
      greater.
    """
    if isinstance(other, Subtitle):
      return cmp(self.number, other.number)
    else:
      return cmp(self.number, other)

  def __str__(self):
    """Returns the String of this object."""
    return (
        'number: %s, iso_code: %s, iso_language: %s, language: %s' %
        (self.number, self.iso_code, self.iso_language, self.language))

  def __repr__(self):
    """Returns the String representation of this object."""
    return (
        "dvd.Subtitle(language='%s', iso_code='%s', iso_language='%s', "
        ' number=%s, strict=%s)' %
        (self.language, self.iso_code, self.iso_language,
         self.number, self.strict))

  def _ValidateOptions(self, language, iso_code, iso_language, number, strict):
    """Validates Subtitle class options.

    Args:
      language: String common language used for subtitles.  Default 'English'.
      iso_code: String ISO language abbreviation code identifier.
        Default 'iso639-2'.
        See http://www.loc.gov/standards/iso639-2/php/code_list.php
      iso_language: String iso-encoded language ID.  Default 'eng'.
      number: Integer subtitle track number.  Default 1.
      strict: Boolean True to enforce strict value checking.  Default False.

    Raises:
      TypeError: If arguments passed are not valid.
      ValueError: If argument values are not valid.
    """
    if (not isinstance(language, str) or
        not isinstance(iso_code, str) or
        not isinstance(iso_language, str)):
      raise TypeError('Expected String arguements: language(%s), '
                      'iso_code(%s), iso_language(%s)' %
                      (language, iso_code, iso_language))
    if not isinstance(number, int):
      raise TypeError('Expected String arguements: number(%s)' % number)
    if strict and number < 0:
      raise ValueError('Number must be positive or 0.')

  def _ProcessLine(self, line):
    """Processes a handbrake log line for subtitle options.

    A Subtitle line in the Handbrake log looks like the following:
        + 1, English (Closed Caption) (iso639-2: eng)
        + 2, Espanol (iso639-2: spa)

    Args:
      line: String containing an subtitle line from handbrake.

    Raises:
      InvalidHandbrakeLogLine: If log line is not in the expected format.

    Returns:
      Tuple containing (<str> language, <str> iso_code, <str> iso_language,
      <int> number).
    """
    try:
      number, language = line.split(',')
      language, iso = language.strip().split(' ', 1)
      iso = iso[iso.rfind('(')+1:iso.rindex(')')].strip()
      iso_code, iso_language = iso.split(':')
      language = language.strip()
      iso_code = iso_code.strip()
      iso_language = iso_language.strip()
      number = int(number.split()[-1])
    except ValueError, error:
      raise InvalidHandbrakeLogLine('ProcessLine failure: %s, %s' %
                                    (error, line))
    return (language, iso_code, iso_language, number)

  def ParseHandbrakeLine(self, line):
    """Parses a title's audio line from Handbrake, and sets attributes.

    This will parse a Handbrake subtitle line, and set this subtitle object to
    the values determined from the line.

    A Subtitle line in the Handbrake log looks like the following:
        + 1, English (Closed Caption) (iso639-2: eng)
        + 2, Espanol (iso639-2: spa)

    Args:
      line: String containing an subtitle line from handbrake.

    Raises:
      InvalidHandbrakeLogLine: If log line is not in the expected format.
    """
    language, iso_code, iso_language, number = self._ProcessLine(line)
    try:
      self._ValidateOptions(language, iso_code, iso_language,
                            number, self.strict)
    except (TypeError, ValueError), error:
      raise InvalidHandbrakeLogLine(
          'Subtitle log line not parsed correctly: %s, line: %s' %
          (error, line))
    self.language = language
    self.iso_code = iso_code
    self.iso_language = iso_language
    self.number = number


class Title(object):
  """Contains information for a given title on a DVD.

  Attributes:
    video_tile_set: Integer representing the Video Tile Set (vts).  A VTS is a
      group of related video titles having similar display format (standard
      screen or wide screen) or aspect ratio.  Default 1.
    number: Integer DVD title number of this title.  Default 1.
    cell_start: Integer cell start for title.  Default 0.  A cell is a unit of
      playback of real-time data and is uniquely identified by a set of numbers.
    cell_end: Integer cell end for title.  Default 0.  A cell is a unit of
      playback of real-time data and is uniquely identified by a set of numbers.
    cell_blocks: Integer number of DVD data blocks that the cells use for this
      title.  Default 0.
    duration: Datetime.datetime object that contains the total playback duration
      for this title.  Default 00:00:00.
    horizontal_size: Integer horizontal size of video.  Default 720.
    vertical_size: Integer vertical size of video.  Default 480.
    aspect_ratio: Float calculated aspect ratio for video.  Default 1.33.
    frame_rate: Float frame rate for video.  Default 29.970.
    autocrop_top: Integer recommended top cropping for title.  Default 0.
    autocrop_bottom: Integer recommended bottom cropping for title.  Default 0.
    autocrop_left: Integer recommended left cropping for title.  Default 0.
    autocrop_right: Integer recommended right cropping for title.  Default 0.
    chapters: List of Chapter objects for this title.
    audio: List of Audio objects for this title.
    subtitles: List of Subtitle objects for this title.
    combining: Boolean True if interlacing or telecined video is detected.
      Default False.
    strict: Boolean True to enforce strict value checking.  Default False.
  """

  def __init__(self, video_tile_set=1, number=1, cell_start=0, cell_end=0,
               cell_blocks=0, duration='00:00:00', horizontal_size=720,
               vertical_size=480, aspect_ratio=1.33, frame_rate=29.970,
               autocrop_top=0, autocrop_bottom=0, autocrop_left=0,
               autocrop_right=0, combining=False, chapters=None, audio=None,
               subtitles=None, strict=False):
    """Initialize title data.

    Args:
      video_tile_set: Integer representing the Video Tile Set (vts).  Default 1.
      number: Integer DVD title number of this title.  Default 1.
      cell_start: Integer cell start for title.  Default 0.
      cell_end: Integer cell end for title.  Default 0.
      cell_blocks: Integer number of DVD data blocks that the cells use for this
      	title.  Default 0.
      duration: Datetime.datetime object that contains the total playback
        duration for this title.  Default 00:00:00.
      horizontal_size: Integer horizontal size of video.  Default 720.
      vertical_size: Integer vertical size of video.  Default 480.
      aspect_ratio: Float calculated aspect ratio for video.  Default 1.33.
      frame_rate: Float frame rate for video.  Default 29.970.
      autocrop_top: Integer recommended top cropping for title.  Default 0.
      autocrop_bottom: Integer recommended bottom title cropping.  Default 0.
      autocrop_left: Integer recommended left cropping for title.  Default 0.
      autocrop_right: Integer recommended right cropping for title.  Default 0.
      combining: Boolean True if interlacing or telecined video is detected.
        Default False.
      chapters: List of Chapter objects to insert into title, or None.
      audio: List of Audio objects to insert into title, or None.
      subtitles: List of Subtitle objects to insert into title, or None.
      strict: Boolean True to enforce strict value checking.  Default False.

    Raises:
      TypeError: If arguments passed to Chapter are not valid.
      ValueError: If argument values are not valid.
    """
    self.strict = strict
    if (not isinstance(video_tile_set, int) or
        not isinstance(number, int) or
        not isinstance(cell_start, int) or
        not isinstance(cell_end, int) or
        not isinstance(cell_blocks, int) or
        not isinstance(horizontal_size, int) or
        not isinstance(vertical_size, int) or
        not isinstance(autocrop_top, int) or
        not isinstance(autocrop_bottom, int) or
        not isinstance(autocrop_left, int) or
        not isinstance(autocrop_right, int)):
      raise TypeError(
          'Expected Integer arguements: video_tile_set(%s), number(%s), '
          'cell_start(%s), cell_end(%s), cell_blocks(%s), '
          'horizontal_size(%s), vertical_size(%s), autocrop_top(%s), '
          'autocrop_bottom(%s), autocrop_left(%s), autocrop_right(%s)' %
          (video_tile_set, number, cell_start, cell_end, cell_blocks,
           horizontal_size, vertical_size, autocrop_top, autocrop_bottom,
           autocrop_left, autocrop_right))
    if (video_tile_set < 0 or horizontal_size < 0 or vertical_size < 0 or
        autocrop_top < 0 or autocrop_bottom < 0 or autocrop_left < 0 or
        autocrop_right < 0):
      raise ValueError('Integer arguments must be positive or 0.')
    if (not isinstance(aspect_ratio, float) or
        not isinstance(frame_rate, float)):
      raise TypeError(
          'Expected Float arguements: aspect_ratio(%s), frame_rate(%s)' %
          (aspect_ratio, frame_rate))
    if isinstance(duration, datetime.datetime):
      self.duration = duration
    elif isinstance(duration, str):
      try:
        hours, minutes, seconds = map(lambda x: int(x), duration.split(':'))
        self.duration = datetime.datetime(1, 1, 1, hours, minutes, seconds)
      except (TypeError, ValueError):
        raise TypeError('Duration format incorrect.')
    else:
      raise TypeError('Duration must be a String or datetime.datetime object.')
    if strict and cell_start > cell_end:
      raise ValueError('cell start should be equal to, or less than cell end.')
    if strict and cell_start < 0:
      raise ValueError('Cell start must be positive or 0.')
    if strict and cell_end < 0:
      raise ValueError('Cell end must be positive or 0.')
    if strict and cell_blocks < 0:
      raise ValueError('Cell blocks must be positive or 0.')
    if strict and number < 0:
      raise ValueError('Number must be positive or 0.')
    self.video_tile_set = video_tile_set
    self.number = number
    self.cell_start = cell_start
    self.cell_end = cell_end
    self.cell_blocks = cell_blocks
    self.horizontal_size = horizontal_size
    self.vertical_size = vertical_size
    self.autocrop_top = autocrop_top
    self.autocrop_bottom = autocrop_bottom
    self.autocrop_left = autocrop_left
    self.autocrop_right = autocrop_right
    self.aspect_ratio = aspect_ratio
    self.frame_rate = frame_rate
    self.combining = combining
    self.chapters = []
    self.audio = []
    self.subtitles = []

    if chapters:
      self.chapters = chapters
    if audio:
      self.audio = audio
    if subtitles:
      self.subtitles = subtitles

  def GetDuration(self):
    """Returns the duration of the chapter as a String."""
    return str(self.duration.time())

  def AddChapter(self, *args):
    """Adds a chapter to the title.

    A chapter may be added by passing a single Chapter object, multiple
    chapter objects; or raw arguments to a Chapter class, which will be
    created and automatically added to the title.  Strict value checking is
    enforced in created Chapter objects.

    Args:
      args: A Chapter object, multiple Chapter objects, or arguements to create
        a Chapter object.

    Returns:
      Boolean True if successful, False otherwise.
    """
    results = True
    if len(args) < 1:
      results = False
    if len(args) == 1:
      if isinstance(args[0], Chapter):
        self.chapters.append(args[0])
      else:
        results = False
    # The number of arguments used to create a Chapter object, exlcuding strict
    # option.
    elif len(args) == 5 and not isinstance(args[0], Chapter):
      try:
        args = list(args)
        args.append(self.strict)
        self.chapters.append(Chapter(*args))
      except (TypeError, ValueError):
        results = False
    else:
      for chapter in args:
        if isinstance(chapter, Chapter):
          self.chapters.append(chapter)
        else:
          results = False
          break
    self.chapters.sort()
    return results

  def AddAudio(self, *args):
    """Adds an audio track to the title.

    An audio track may be added by passing a single Audio object, multiple
    Audio objects; or raw arguements to a Audio class, which will be created and
    automatically added to the title.  Strict value checking is enforced in
    created Audio objects.

    Args:
      args: An Audio object, multiple Audio objects, or arguements to create an
        Audio object.

    Returns:
      Boolean True if successful, False otherwise.
    """
    results = True
    if len(args) < 1:
      results = False
    if len(args) == 1:
      if isinstance(args[0], Audio):
        self.audio.append(args[0])
      else:
        results = False
    # The number of arguments used to create an Audio object, exluding strict
    # option.
    elif len(args) == 6 and not isinstance(args[0], Audio):
      try:
        args = list(args)
        args.append(self.strict)
        self.audio.append(Audio(*args))
      except TypeError:
        results = False
    else:
      for audio in args:
        if isinstance(audio, Audio):
          self.audio.append(audio)
        else:
          results = False
          break
    self.audio.sort()
    return results

  def AddSubtitle(self, *args):
    """Adds a subtitle track to the title.

    A subtitle may be added by passing a single Subtitle object, multiple
    Subtitle objects; or raw arguements to a Subtitle class, which will be
    created and automatically added to the title.  Strict value checking is
    enforced in created Subtitle objects.

    Args:
      args: A Subtitle object, multiple Subtitle objects, or arguements to
        create an Subtitle object.

    Returns:
      Boolean True if successful, False otherwise.
    """
    results = True
    if len(args) < 1:
      results = False
    if len(args) == 1:
      if isinstance(args[0], Subtitle):
        self.subtitles.append(args[0])
      else:
        results = False
    # The number of arguments used to create a Subtitle object, excluding strict
    # options.
    elif len(args) == 4 and not isinstance(args[0], Subtitle):
      try:
        args = list(args)
        args.append(self.strict)
        self.subtitles.append(Subtitle(*args))
      except TypeError:
        results = False
    else:
      for subtitle in args:
        if isinstance(subtitle, Subtitle):
          self.subtitles.append(subtitle)
        else:
          results = False
    self.subtitles.sort()
    return results

  def __cmp__(self, other):
    """Comparator for use with sorting.

    Args:
      other: Title object or Integer to be compared to.

    Returns:
      Integer 1 this object is greater, 0 objects are equal, -1 other object is
      greater.
    """
    if isinstance(other, Title):
      return cmp(self.number, other.number)
    else:
      return cmp(self.number, other)

  def __str__(self):
    """Returns the String of this object."""
    return (
        'video_tile_set: %s, number: %s, cell_start: %s, cell_end: %s, '
        'cell_blocks: %s, duration: %s, horizontal_size: %s, vertical_size: %s,'
        ' aspect_ratio: %s, frame_rate: %s, autocrop_top: %s, '
        'autocrop_bottom: %s, autocrop_left: %s, autocrop_right: %s, '
        'combining: %s, chapters: %s, audio: %s, subtitles: %s' %
        (self.video_tile_set, self.number, self.cell_start, self.cell_end,
         self.cell_blocks, self.GetDuration(), self.horizontal_size,
         self.vertical_size, self.aspect_ratio, self.frame_rate,
         self.autocrop_top, self.autocrop_bottom, self.autocrop_left,
         self.autocrop_right, self.combining, self.chapters, self.audio,
         self.subtitles))

  def __repr__(self):
    """Returns the String representation of this object."""
    return (
        'dvd.Title(video_tile_set=%s, number=%s, cell_start=%s, cell_end=%s, '
        "cell_blocks=%s, duration='%s', horizontal_size=%s, vertical_size=%s, "
        'aspect_ratio=%s, frame_rate=%s, autocrop_top=%s, autocrop_bottom=%s, '
        'autocrop_left=%s, autocrop_right=%s, combining=%s, chapters=%s, '
        'audio=%s, subtitles=%s, strict=%s)' %
        (self.video_tile_set, self.number, self.cell_start, self.cell_end,
         self.cell_blocks, self.GetDuration(), self.horizontal_size,
         self.vertical_size, self.aspect_ratio, self.frame_rate,
         self.autocrop_top, self.autocrop_bottom, self.autocrop_left,
         self.autocrop_right, self.combining, self.chapters, self.audio,
         self.subtitles, self.strict))


class Dvd(object):
  """Contains all information that can be obtained from a DVD via Handbrake.

  Attributes:
    name: String name of the DVD.
    titles: List containing Titles on the DVD.
    strict: Boolean True to enforce strict value checking.  Default False.
  """

  def __init__(self, name=None, titles=None, strict=False):
    """Intalize Dvd data.

    Args:
      name: String name of the DVD.  Default: Current datetime.
      titles: List of Title objects for this DVD.  Default None.
      strict: Boolean True to enforce strict value checking.  Default False.
    """
    self.strict = strict
    if not name:
      time = datetime.datetime.now()
      self.name = time.strftime('%Y-%m-%d_%H-%M-%S')
    else:
      self.name = name
    self.titles = []
    if titles:
      self.AddTitle(*titles)

  def AddTitle(self, *args):
    """Adds a Title to the DVD.

    A title may be added by passing a single Title object, multiple Title
    objects.

    Args:
      args: Title object or multiple Title objects.

    Returns:
      Boolean True if successful, False otherwise.
    """
    results = True
    if len(args) < 1:
      results = False
    else:
      for title in args:
        if isinstance(title, Title):
          self.titles.append(title)
        else:
          results = False
          break
    self.titles.sort()
    return results

  def GetTitle(self, title_number):
    """Returns a Title object with the given title number.

    Args:
      title_number: Integer title number to find for title object to return.

    Raises:
      TitleNotFoundError: If the given title number is not in the DVD.

    Returns:
      Title object for the given title number.
    """
    for title in self.titles:
      if title.number == title_number:
        return title
    raise TitleNotFoundError('Title %s not in DVD.')

  def ProcessHandbrakeAnalysis(self, analysis):
    """Processes output (--title 0) from handbrake, creating a full DVD object.

    Args:
      analysis: List containing all of the lines from a HandBrake full title
        scan (--title 0), including new lines.
    """
    self.titles = []
    log = ''.join(analysis).splitlines()
    titles, dvd_name = self._IndexHandbrakeLog(log)
    for title_index in xrange(len(titles)):
      if title_index == len(titles)-1:
        self._ProcessTitle(log[titles[title_index]:])
      else:
        self._ProcessTitle(log[titles[title_index]:titles[title_index+1]])
    if dvd_name:
      self.name = dvd_name

  def _ProcessTitle(self, title_log):
    """Processes title information for a given title section in Handbrake log.

    Parses all the log information for a particular title, creating and adding a
    corresponding title object to this DVD object.

    Args:
      title_log: List containing Strings of the Handbrake log specific to an
        individual title.
    """
    title, chapter_index, audio_index, subtitle_index = (
        self._ExtractTitleFromLog(title_log))
    if chapter_index:
      title.AddChapter(*self._ProcessTitleSection(
          title_log[chapter_index:], Chapter))
    if audio_index:
      title.AddAudio(*self._ProcessTitleSection(
          title_log[audio_index:], Audio))
    if subtitle_index:
      title.AddSubtitle(*self._ProcessTitleSection(
          title_log[subtitle_index:], Subtitle))
    self.AddTitle(title)

  def _ProcessTitleSection(self, log, line_object):
    """Processes a given title section, using the provided callback method.

    A title section in the Handbrake log is any line starting at an indentation
    of at least 4 spaces and a '+'.  New sections start at an indentation of two
    spaces and a '+'.  A new title also starts if a new line does not start
    with a space.  This assumes that the log starts with a valid section.

        + valid section (this is processed)
      + New section
        + valid section
    + New title

    Args:
      log: List of Strings containing title log section to process.
      line_object: Class that can be instantiated and a ParseHandbrakeLine
        method called.

    Returns:
      List containing processed objects for each line using the line_object
      class or an empty list.
    """
    results = []
    for line in log:
      if line.startswith('  +') or not line.startswith(' '):
        break
      else:
        section_object = line_object(strict=self.strict)
        section_object.ParseHandbrakeLine(line)
        results.append(section_object)
    return results

  def _ExtractTitleFromLog(self, log):
    """Extracts title information from Handbrake title log section.

    Calculated chapter, audio and subtitle indexes are automatically adjusted by
    1.

    Args:
      log: List of Strings making up a 'title' section of a Handbrake log.  A
        title section is all data between the '+ title #:' lines.

    Returns:
      Tuple  (<Title> title, <int> chapter, <int> audio, <int> subtitle),
      containing a title object and indexes for chapter, audio and subtitle.  If
      an index is not found, None is returned for that index.
    """
    combining = False
    chapter_index, audio_index, subtitle_index = None, None, None

    for index in xrange(len(log)):
      if log[index].startswith('+ title '):
        title_number = int(log[index].split(':')[0].split(' ')[2])
      if log[index].startswith('  + vts'):
        video_tile, cell_start, cell_end, cell_blocks = (
            self._ParseVideoTileSetLine(log[index]))

      if log[index].startswith('  + duration'):
        duration = self._ParseDurationLine(log[index])

      if log[index].startswith('  + size'):
        horizontal_size, vertical_size, aspect_ratio, frame_rate = (
            self._ParseSizeLine(log[index]))

      if log[index].startswith('  + autocrop'):
        top, bottom, left, right = self._ParseAutoCropLine(log[index])
      if log[index].startswith('  + chapters'):
        chapter_index = index + 1
      if log[index].startswith('  + audio tracks'):
        audio_index = index + 1
      if log[index].startswith('  + subtitle tracks'):
        subtitle_index = index + 1
      if log[index].startswith('  + combining detected'):
        combining = True

    title = Title(video_tile, title_number, cell_start, cell_end, cell_blocks,
                  duration, horizontal_size, vertical_size, aspect_ratio,
                  frame_rate, top, bottom, left, right, combining, self.strict)
    return (title, chapter_index, audio_index, subtitle_index)

  def _ParseVideoTileSetLine(self, line):
    """Parses a title's vts line from Handbrake.

    A vts line from Handbrake is in the following format:
      + vts 1, ttn 1, cells 0->24 (1939167 blocks)

    Args:
      line: String containing the '+ vts' line from Handbrake.

    Returns:
      Tuple (<str video_tile_set>, <int cell_start>, <int cell_stop>,
      <int cell_blocks>), ready for use in Title classes.
    """
    video_tile, unused_title, cells = line.split(',')
    video_tile = int(video_tile.split()[-1])
    cells = cells.split()
    cell_start, cell_end = map(lambda x: int(x), cells[1].split('->'))
    cell_blocks = int(cells[2][1:])
    return (video_tile, cell_start, cell_end, cell_blocks)

  def _ParseDurationLine(self, line):
    """Parses a title's duration line from Handbrake.

    A duration line from Handbrake is in the following format:
      + duration: 01:26:38

    Args:
      line: String containing the '+ duration' line from Handbrake.

    Returns:
      String duration of the title.
    """
    return line.split()[-1]

  def _ParseSizeLine(self, line):
    """Parses a title's size line from Handbrake.

    A size line from Handbrake is in the following format:
      + size: 720x480, aspect: 1.78, 23.976 fps

    Args:
      line: String containing the '+ size' line from Handbrake.

    Returns:
      Tuple (<int horizontal_size>, <int vertical_size>, <float aspect_ratio>,
      <float frame_rate>), ready for use in Title classes.
    """
    size, aspect, frame_rate = line.split(',')
    size = size.split(': ')[-1].split('x')
    horizontal_size, vertical_size = map(lambda x: int(x), size)
    aspect = float(aspect.split()[-1])
    frame_rate = float(frame_rate.split()[0])
    return (horizontal_size, vertical_size, aspect, frame_rate)

  def _ParseAutoCropLine(self, line):
    """Parses a title's autocrop line from Handbrake.

    An autocrop line from Handbrake is in the following format:
      + autocrop: 0/0/0/0

    Args:
      line: String containing the '+ autocrop' line from Handbrake.

    Returns:
      Tuple (<int top>, <int bottom>, <int left>, <int right>) croppings, ready
      for use in Title classes.
    """
    crops = line.split()[-1].split('/')
    return map(lambda x: int(x), crops)

  def _IndexHandbrakeLog(self, log):
    """Indexes the HandBrake log for key positions and values.

    Args:
      log: List of Strings containing the HandBrake full title scan.

    Returns:
      Tuple containing (<list titles>, <str dvd_name>), where titles is a list
      of Integers containing the start of each title in the log.  dvd_name is
      the parsed name of the DVD disc or None.
    """
    dvd_name = None
    titles = []
    for index in xrange(len(log)):
      if log[index].startswith('Scanning title '):
        continue
      if log[index].startswith('Opening'):
        dvd_name = self._DetermineDvdName(log[index])
      if log[index].startswith('+ title'):
        titles.append(index)
    return (titles, dvd_name)

  def _DetermineDvdName(self, name_line):
    """Determines the DVD's title from HandBrake Source file line.

    HandBrake's DVD source file is in the following format:
      'Opening <path>...'

    Args:
      name_line: String line containing 'Opening XXX', where XXX is the file
        that is being processed by handbrake.

    Returns:
      String containing the parsed DVD name, or None.
    """
    results = None
    if name_line.startswith('Opening '):
      source_file = name_line.split('Opening ')[1][:-3]
      if os.path.basename(source_file):
        results = os.path.basename(source_file)
      else:
        results = os.path.split(os.path.dirname(source_file))[1]
    return results

  def __str__(self):
    """Returns the String of this object."""
    return 'name: %s, titles: %s' % (self.name, self.titles)

  def __repr__(self):
    """Returns the String representation of this object."""
    return ("dvd.Dvd(name='%s', titles=%s, strict=%s)" %
            (self.name, self.titles, self.strict))
