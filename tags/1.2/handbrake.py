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
"""Python HandBrake class for HandBrakeCLI interactions.

Enables the easy use (and re-use) of HandBrakeCLI in Python scripts.
"""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'
__version__ = '1.0'

import copy
import datetime
import os
import subprocess
import tempfile
import abs_path
import dvd
import handbrake_options


class Error(Exception):
  """Generic HandBrake exception."""


class BinaryNotFoundError(Error):
  """The HandBrakeCLI binary could not be found."""


class OptionError(Error):
  """Thrown when invalid options are encountered in the handbrake object."""


class ExecuteError(Error):
  """An error occurred while executing handbrakeCLI."""


class VersionError(Error):
  """A version mis-match was detected."""


class EncodeError(Error):
  """An error occurred while setting up the encoding process."""


class HandBrake(object):
  """Class to interact with HandBrakeCLI.

  Attributes:
    __VERSION: String supported version of handbrake.
    __SEARCH_PATHS: List containing general known locations of HandBrake Binary.
    _critical_version: Boolean True if version mis-match should throw exception.
    _location: String full path to binary.
    _log: List containing log information from executing HandBrakeCLI.
    options: Options object containing handbrake_options.Options to use.
    dvd: dvd.Dvd object containing parsed DVD title information.
  """
  __VERSION = 'HandBrake 0.9.3 (2008112300)'
  __SEARCH_PATHS = ['/usr/bin', '/usr/local/bin', '/bin', '/opt/bin']

  def __init__(self, critical_version=True):
    """Initalizes default HandBrakeCLI object.

    Args:
      critical_version: Boolean True if a version mis-match should be fatal.
    """
    self._critical_version = critical_version
    self._location = None
    self._log = []
    self.options = handbrake_options.Options()
    self.dvd = dvd.Dvd()

  def _FindBinaryLocation(self, location=None):
    """Determines the location of the HandBrake Binary.

    If a location is specified but not found, the default search path is used
    to find the binary.

    Args:
      location: String full path to the HandBrake binary if overriding default
        search locations.

    Raises:
      BinaryNotFoundError: If the handbrake binary could not be found.

    Returns:
      String containing the full path to the HandBrakeCLI binary.
    """
    if not location or not os.path.exists(location):
      for search_path in self.__SEARCH_PATHS:
        location = os.path.join(search_path, 'HandBrakeCLI')
        if os.path.exists(location):
          break
      else:
        raise BinaryNotFoundError('Handbrake binary not found!')
    return location

  def _ValidateOptions(self, options):
    """Validates a given list of options.

    Args:
      options: List containing handbrake_options.options.Option objects.

    Returns:
      Boolean True if the options are valid options, False otherwise.
    """
    results = True
    if isinstance(options, list):
      for option in options:
        if not isinstance(option, handbrake_options.options.Option):
          results = False
          break
    else:
      results = False
    return results

  def _WriteLog(self, log):
    """Writes a clean handbrake log, removing the percentage indicators.

    This removes the percent complete indication lines, as well as stripping
    newline characters from the end of each line; then truncates and writes to
    the internal log.

    Args:
      log: List of log lines from HandBrake Execution.
    """
    self._log = []
    for line in log:
      if not line.startswith('\rEncoding: task'):
        self._log.append(line)

  def _Execute(self, options):
    """Excutes handbrake with given options set.

    Execute will automatically clean the handbrake log of any processing
    indicators.

    Args:
      options: List of handbrake_options.Options to use with CLI.

    Raises:
      ExecuteError: If there was a problem excuting the handbrakeCLI.
    """
    command = [self._location]
    if self._ValidateOptions(options):
      for option in options:
        command.extend(option.Command())
      try:
        # Subprocess works at OS level, so cStringIO file objects won't work.
        temp_file = tempfile.TemporaryFile()
        results = subprocess.call(command, stdout=temp_file,
                                  stderr=temp_file, shell=False)
        temp_file.seek(0)
        self._WriteLog(temp_file.readlines())
        temp_file.close()
      except (OSError, IOError), error:
        raise ExecuteError('CLI command failed: %s' % error)
      if results != 0:
        raise ExecuteError('HandBrakeCLI exited with exitcode of %s.' % results)
    else:
      raise ExecuteError('No options given to HandBrakeCLI.')

  def _CheckVersion(self):
    """Checks handbrake binary version against the supported version.

    Raises:
      VersionError: If critical_version is enabled, and there is a version
        mis-match.
      ExecuteError: If there is a problem executing the CLI.
    """
    update_option = copy.deepcopy(self.options.general_update)
    update_option.SetValue(True)
    self._Execute([update_option])
    if not self._log or not self._log[0].startswith(self.__VERSION):
      if self._critical_version:
        raise VersionError('Version mis-match: %s is supported.' %
                           self.__VERSION)

  def Connect(self, location=None):
    """Locates and verifies the HandBrake Binary to use.

    Will attempt to use the HandBrake binary specified in the arguments.  If no
    location is specified, the binary is searched for on the default search
    path (self.__SEARCH_PATHS).

    Args:
      location: String location of handbrake binary.  Default None.

    Raises:
      BinaryNotFoundError: If the handbrake binary does not exist.
      VersionError: If a version mis-match is detected, and critical version
        errors are enabled.
    """
    self._location = self._FindBinaryLocation(location)
    self._CheckVersion()

  def GetDvdInformation(self, dvd_image):
    """Generates a dvd.Dvd object from a given dvd image.

    Args:
      dvd_image: String full path to file/dir for DVD image.

    Raises:
      ExecuteError: If there is a problem executing the CLI.
    """
    input_file = copy.deepcopy(self.options.file_input)
    full_scan = copy.deepcopy(self.options.file_title)
    input_file.SetValue(abs_path.AbsPath(dvd_image))
    full_scan.SetValue(0)
    self._Execute([input_file, full_scan])
    self.dvd.ProcessHandbrakeAnalysis(self._log)

  def _SetChapterOptions(self, start, end):
    """Sets chapter options for Encode.  Should not be called directly.

    Args:
      start: Integer chapter start or None.
      end: Integer chapter end or None.

    Raises:
      EncodeError: If start > end or start == end.
    """
    if start is not None and end is not None:
      if start > end:
        raise EncodeError(
            'start (%s) must be less than end (%s).' % (start, end))
      else:
        self.options.file_chapters.SetValue('%s-%s' % (start, end))

  def _SetEncodeOptions(self, source, output, title):
    """Sets encoding options for Encode.  Should not be called directly.

    Args:
      source: String full path to input directory.
      output: String full path to output file/directory.
      title: Integer/String title number to encode.  'longest' for longest
        title.

    Raises:
      EncodeError: If input/output directories are invalid.
    """
    source = abs_path.AbsPath(source)
    output = abs_path.AbsPath(output)
    if not os.path.exists(source):
      raise EncodeError('Input directory (%s) does not exist!' % source)
    if not os.path.exists(os.path.dirname(output)):
      raise EncodeError('Output directory (%s) does not exist!' % output)
    self.options.file_input.SetValue(source)
    self.options.file_output.SetValue(output)
    if isinstance(title, int):
      self.options.file_title.SetValue(title)
      self.options.file_longest_title.SetValue(False)
    else:
      self.options.file_longest_title.SetValue(True)
      self.options.file_title.SetValue(self.options.file_title.default)
      self.options.file_chapters.SetValue(self.options.file_chapters.default)

  def Encode(self, source, output, title, start=None, end=None):
    """Encodes a single title for a given dvd.

    This will not attempt a file encoding if the destination file already
    exists.  Using the 'longest' option will disable start and end options.
    Both start and end options must be specified if either is used.

    Args:
      source: String full path to input directory.
      output: String full path to output file.
      title: Integer/String title number to encode.  Use Integer, or 'longest'
        to encode the longest title in the file (good for movies).
      start: Integer chapter start, inclusive.  Default None (all chapters).
      end: Integer chapter end, inclusive.  Default None (all chapters).

    Returns:
      A tuple (<Boolean success>, <datetime.timedelta execution_time>,
      <Integer/String title_encoded>, <list encode_log>).

    Raises:
      TypeError: If the specified arguments were invalid.
      ValueError: If start/end values were invalid.
      EncodeError: If the encoding failed for some reason.
    """
    self._SetChapterOptions(start, end)
    self._SetEncodeOptions(source, output, title)
    success = False
    execution_time = 0
    log = []

    if not os.path.exists(abs_path.AbsPath(output)):
      start_time = datetime.datetime.now()
      self._Execute(self.options.all)
      execution_time = datetime.datetime.now() - start_time
      success = True
      log.extend(self._log)
    else:
      log.append('Title (%s) Will not overwrite output file: %s.' %
                 (title, output))
    return (success, execution_time, title, log)

  def EncodeAll(self, source, output_dir, time_limit=None):
    """Encodes all titles for a dvd.

    This will encode all the titles in a given file / directory using the last
    directory of the input file as the prefix.  If a time limit is specified,
    any title less than the time limit will be skipped.

    Files will be stored as: output/input-#.format.  Format is determined from
    the handbrake format option.

    time_limit should only use hours, minutes, seconds.  Create an object with
    the year, month and day set to 1.  For a 2 minute time_limit:
    datetime.datetime(1, 1, 1, 0, 2, 0)

    Args:
      source: String full path to input directory.
      output_dir: String full path to output directory.
      time_limit: datetime.datetime object time limit in seconds.  Any title
        shorter than this number will be ignored.

    Returns:
      A list of tuples, (<Boolean success>, <datetime.timedelta execution_time>,
      <Integer/String title_encoded>, <list encode_log>).
    """
    skip_string = 'Skipping Title %s (%s), shorter than %s.'
    results = []
    self.GetDvdInformation(source)
    for title in self.dvd.titles:
      if time_limit and title.duration < time_limit:
        limit_length = str(time_limit.time())
        results.append(
            (False, datetime.timedelta(0, 0, 0), title.number,
             [skip_string % (title.number, title.GetDuration(), limit_length)]))
        continue
      output_file = ('%s%s [Title %s].%s' %
                     (abs_path.AbsPath(output_dir), self.dvd.name, title.number,
                      self.options.file_format.value))
      results.append(self.Encode(source, output_file, title.number))
    return results
