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
"""Command line multiple dvd encoder.

Encodes all dvd's in a given directory and subdirectories using the handbrake
module.
"""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'
__version__ = '1.2'

import ConfigParser
import datetime
import logging
import optparse
import os
import smtplib
import sys
import abs_path
import handbrake


class Error(Exception):
  """Generic encode_dvd error."""


class ConfigError(Error):
  """There was a problem processing the configuration file."""


class OptionProcessError(Error):
  """Error processing command line options."""


class EmailError(Error):
  """Error sending e-mail to given recipients."""


class HandbrakeError(Error):
  """Error using handbrake."""


class EncodeDvdOptions(object):
  """Commnadline options for encode_dvd.

  Attributes:
    parser: OptionParser object containing valid encode_dvd options.
  """
  USAGE = """

  Encode DVD %s by %s.

  Encodes a given DVD rip directory to an output directory.

  DVD rip Directory:
    - A DVD Rip is a directory that contains a VIDEO_TS file.
    - DVD rip Directory may be only a single DVD rip.
    - DVD rip Directory may contain multiple DVD rips (including recursively)
      as long as there are no nested DVD rips (rips inside of rips).

  Encode DVD Config:
    --config can specify filename OR full path (default: encode_dvd.config).
    - Configuration file is found in the following order:
      1) full path (if used)
      2) ~/.encode-dvd/
      3) /etc/encode-dvd/

  Encoding Output:
    Encodes will be written to the output directory in the following format:

    [name] [Title X] <[Chapters Y-Z]>.format

    Where:
      name: Source DVD rip directory basename.
      Title: Source DVD Title encoded.
      Chapters: (optional) Chapters encoded for the Title.  Only used when
        encoding specific Chapters for a specific Title.
      format: File format extension, which is determined by using the
        FILE_FORMAT option in encode_dvd.config or automatically by handbrake
        based on encoding settings.

  Logging (default: /var/log/encode-dvd):
    full_encodes.log:
      Contains a list of all the DVD directories automatically encoded
      sucessfully.  This DOES NOT contain DVD's that were encoded specifically
      with the --title option.  If you want to re-encode, delete DVD the line
      from this file.
    encode_dvd.log:
      Log file containing detailed information on what encode DVD is doing.
      Generally used for tracking cronjob progress, or debugging encodes (Good
      for tracking down those DVD's that write all episodes as a single title.
      See --title, --chapter-start, --chapter-end options).

  E-mail Notification:
    - Encode DVD will run slient with e-mail notification (cronjob safe) unless:
      1) Bad options are passed to it when run
      2) --list option is used
      3) --title option is used

  Watching a directory for new DVD rips to encode:
    - /home/user/bin/encode_job:
        #!/bin/bash
        ENCODE='/opt/bin/encode-dvd'
        SOURCE='/Videos/DVD Images/'
        OUTPUT='/Videos/Encodes/'
        EMAIL='your@email.com'
        MIN_TIME=120
        # If there is no encode process running under this user
        if [ `pgrep -c encode-dvd` -eq 0 ]; then
          ${ENCODE} --source "${SOURCE}" --destination "${OUTPUT}" \\
            --email "${EMAIL}" --time ${MIN_TIME} &
        fi
     - Crontab:
         0 * * * * /home/user/bin/encode_job
  """ % (__version__, __author__)

  def __init__(self):
    """Initalizes EncodeDvdOptions."""
    self.parser = optparse.OptionParser(usage=self.USAGE)
    self.parser.add_option(
        '-s', '--source', metavar='FILE', dest='source',
        help='Full path to source directory containing DVD rip or DVD rips to '
        'encode.  Required.')
    self.parser.add_option(
        '-d', '--destination', metavar='FILE', dest='destination', default=None,
        help='Full path to destination directory for encoded files.  Required '
        'if not using the --list option.')
    self.parser.add_option(
        '-e', '--email', action='store', type='string', dest='email',
        default=None, help='E-mail address for notification of encoding '
        'process.  If not specified, e-mail notification is disabled.  '
        'Note: e-mail is sent VIA localhost only!')
    self.parser.add_option(
        '-t', '--time', action='store', type='int', dest='time', default=120,
        help='Minimum length of title on DVD to encode in seconds.  Titles '
        'under this length are skipped.  Default 120 seconds (2 minutes), '
        'ignored if encoding a specific title (--title).')
    self.parser.add_option(
        '-b', '--hardburn-subtitles', action='store', type='int',
        dest='hard_subtitles', default=None, help='Force subtitles to be '
        'hard-burned into the video (cannot be turned off).  Good for output '
        'formats or media players that do not support subtitles.  Track for '
        'subtitle is determined by track number used with this option.  Use '
        '--list for subtitle information for a DVD.  --forced-subtitles option '
        'will be ignored.')
    self.parser.add_option(
        '-f', '--forced-subtitles', action='store_true', dest='force_subtitles',
        default=False, help='Encode subtitles for rips where they are forced by'
        ' the movie, or are less than 10% of the movie length.  Language for '
        'subtitles is determined by the SUBTITLES_NATIVE_LANGUAGE handbrake '
        'option.  Requires compatable media player.  If your media player does '
        'not play subtitles, try the --hardburn-subtitles option.')
    self.parser.add_option(
        '-a', '--chapter-start', action='store', type='int',
        dest='chapter_start', default=None, help='Start encoding at specified '
        'chapter (inclusive).  Only used with --title option.')
    self.parser.add_option(
        '-n', '--chapter-end', action='store', type='int', dest='chapter_end',
        default=None, help='End encoding at specified chapter (inclusive).  '
        'Only used with --title option.')
    self.parser.add_option(
        '-i', '--title', action='store', type='int', dest='title', default=None,
        help='Encode a specified title instead of all titles for rip.  Must use'
        ' with --chapter-start and --chapter-end.  Useful to encode a series '
        'which contains all episodes on a single track.  If you are using this '
        'option, you should specify a SINGLE DVD to encode, otherwise all DVDs '
        'will be encoded with the same start/end options.  --time option will '
        'be ignored.')
    self.parser.add_option(
        '-c', '--config', action='store', type='str', dest='config',
        default='encode_dvd.config', help='Alternative location of '
        'encode_dvd.config.  Useful for encoding in different formats.  '
        'Order of config search: 1) Custom location specified, '
        '2) ~/.encode-dvd/<config>, 3) /etc/encode-dvd/<config>.')
    self.parser.add_option(
        '-l', '--list', action='store_true', dest='list', default=False,
        help='List title information for given DVD source.  Can list multiple '
        'DVD title information at once by specifying directory with multiple '
        'rips inside of it.')
    self.parser.add_option(
        '-q', '--quiet', action='store_true', dest='quiet', default=False,
        help='Disable output to screen.  Only useful for --title option.')
    self.parser.add_option(
        '-g', '--ignore', action='store_true', dest='ignore', default=False,
        help='Ignore validation checks when specifying --chapter-start and '
        '--chapter-end.  This will force encoding, possibly causing unexpected '
        'handbrake failures.  Use if DVD is mis-reporting title and chapter '
        'indexes, but you know they exist.')


class EncodeDvdConfigParser(object):
  """Handles configuration parsing for encode_dvd.

  Attributes:
    parser: ConfigParser.ConfigParser object.
  """

  def __init__(self):
    """Initialize EncodeDvdConfigParser."""
    self.parser = ConfigParser.ConfigParser()

  def ProcessConfig(self, config='encode_dvd.config'):
    """Process a config file setting up logs and generating a handbrake object.

    Args:
      config: String location of config file to process.

    Raises:
      ConfigError: If there is an error processing the configuration file.

    Returns:
      Tuple (handbrake.HandBrake object, String full encodes log) with
      configuration options set.
    """
    try:
      config_file = open(self.FindConfigFile(config))
      self.parser.readfp(config_file)
      config_file.close()
    except (ConfigParser.Error, IOError), error:
      raise ConfigError('Could not read configuration file: %s' % error)
    if not self.parser.has_section('handbrake'):
      raise ConfigError('No handbrake encoding options specified in config!')
    if not self.parser.has_section('logging'):
      raise ConfigError('No logging options specified in config!')

    return (self._GetHandbrakeObject(), self._InitializeLogging())

  def _InitializeLogging(self):
    """Sets up logging for encode_dvd and determines full encodes log.

    Raises:
      ConfigError: If there is an error processing the configuration file.

    Returns:
      String containing the full encodes log file.
    """
    try:
      directory = self.parser.get('logging', 'LOG_DIRECTORY')
      full = self.parser.get('logging', 'LOG_FULL')
      log = self.parser.get('logging', 'LOG_ENCODE')
      log_level = self.parser.get('logging', 'LOG_LEVEL')
    except ConfigParser.Error, error:
      raise ConfigError('Failed to load config file: %s' % error)
    if log_level not in dir(logging):
      raise ConfigError('Logging level must be specified!')
    directory = abs_path.AbsPath(directory)
    logging.basicConfig(
        filename='%s%s' % (directory, log),
        format='%(asctime)s %(levelname)s[%(name)s]: %(message)s',
        level=getattr(logging, log_level))
    return '%s%s' % (directory, full)

  def _GetHandbrakeObject(self):
    """Generates a handbrake object from the configuration file.

    Raises:
      ConfigError: If there is an error processing the configuration file.

    Returns:
      handbrake.HandBrake object with configuration options set.
    """
    hb = handbrake.HandBrake()
    for key, value in self.parser.items('handbrake'):
      try:
        getattr(hb.options, key.lower()).SetValue(self.DetermineType(value))
      except (handbrake.Error, TypeError, ValueError), error:
        raise ConfigError('Failed to load config file: %s' % error)
    return hb

  def DetermineType(self, value):
    """Determines a given configuration value datatype.

    Args:
      value: String data to determine datatype.

    Returns:
      Data value in the guessed datatype.
    """
    # For datatypes forced interpertation as Strings.
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
      return value[1:-1]
    if value.lower() == 'true':
      return True
    if value.lower() == 'false':
      return False
    try:
      return int(value)
    except ValueError:
      pass
    try:
      return float(value)
    except ValueError:
      pass
    return value

  def FindConfigFile(self, config):
    """Determines the location of a specified configuration file.

    The path will be expanded and converted to an absolute path.  If not found,
    the config is attempted to be found in the current user's home directory in
    ~/.encode-dvd/ and finally /etc/encode-dvd.

    Args:
      config: String configuration file to locate and verify.

    Raises:
      ConfigError: If the configuration file could not be located.

    Returns:
      The absolute path containing the configuration file to use.
    """
    file_path = abs_path.AbsPath(config)
    if not os.path.exists(file_path):
      file_path = abs_path.AbsPath(os.path.join('~', '.encode-dvd', config))
      if not os.path.exists(file_path):
        file_path = os.path.join('/etc', 'encode-dvd', config)
        if not os.path.exists(file_path):
          raise ConfigError('The configuration file could not be located.')
    return file_path


class DvdContainerGenerator(object):
  """Handles finding and returning valid DVD titles from a given directory.

  Attributes:
    sources: List containing valid DVD Containers found.
  """

  def __init__(self):
    """Initialize DvdContainerGenerator."""
    self.sources = []

  def _DvdFilter(self, arg, dirname, fnames):
    """Determines if a directory is a valid DVD container.

    A directory is a valid DVD container, if a file exists in a given
    directory called 'VIDEO_TS'.

    Arguments are specified by os.path.walk.

    Args:
      arg: List containing validated directories (This can be anything).
      dirname: String the current directory.
      fnames: List containing all current files in current directory.
    """
    if 'VIDEO_TS' == os.path.basename(dirname).upper():
      arg.append(abs_path.AbsPath(os.path.dirname(dirname)))

  def GenerateDvdContainers(self, path):
    """Generates a list containing all valid source directories for encoding.

    A valid source directory is specified as a directory whose direct children
    contain a VIDEO_TS directory.  Any directories that are skipped are logged
    with an explanation as to why.

    If logging is used, it will automatically remove DVD containers that have
    already been processed.

    A list containing full paths of source directories to use for encoding is
    stored in self.sources.

    Args:
      path: String path to the source directory to find containers.
    """
    self.sources = []
    os.path.walk(path, self._DvdFilter, self.sources)


class Mail(object):
  """Handles e-mailing notifications to users.

  Attributes:
    HOST: String e-mail host to send mail to.  Default localhost.
  """
  HOST = 'localhost'

  def __init__(self, address=None):
    """Initializes mail object with given e-mail address.

    Args:
      address: String e-mail address to use for FROM and TO headers.
    """
    self.address = address

  def SendMail(self, subject, body):
    """Sends an e-mail to a given recipient.

    Args:
      subject: String subject to use for e-mail.
      body: String body of e-mail.  Must use UNIX newlines.

    Raises:
      EmailError: If e-mail failed to be sent.
    """
    if self.address:
      try:
        smtp = smtplib.SMTP(self.HOST)
        smtp.sendmail(self.address, self.address,
                      'Subject: %s\n\n%s' % (subject, body))
        smtp.close()
      except (smtplib.SMTPException, smtplib.socket.error), error:
        raise EmailError('Could not send e-mail: ' + str(error))


class EncodeDvd(object):
  """Encodes all DVD's in a given directory/sub directory.

  Attributes:
    _log: An instantiated file object for logging.
    _log_full: An instantiated file object for full file encodes.
    _log_full_index: Dictionary containing in-memory list of full file encodes.
    parser: An instantiated EncodeDvdOptions parser object.
    config: An instantiated EncodeDvdConfigParser object.
    handbrake: handbrake.HandBrake object used for encoding.
    dvd_containers: An instantiated DvdContainerGenerator object to generate
      valid DVD Containers for a given source path.
    sources: List containing valid non-processed sources to process.
    mail: An instantiated Mail object to send notification e-mails.
    silent: Boolean True to repress printing to screen.
  """

  def __init__(self):
    """Initalizes EncodeDvd."""
    self._log = None
    self._log_full = None
    self._log_full_index = {}
    self.parser = EncodeDvdOptions().parser
    self.config = EncodeDvdConfigParser()
    self.handbrake = None
    self.dvd_containers = DvdContainerGenerator()
    self.sources = []
    self.mail = None
    self.silent = False

  def __del__(self):
    """Closes open file handles when EncodeDvd is stopped."""
    if self._log_full:
      self._log_full.close()

  def _Log(self, message, critical=False):
    """Writes a log message to the log file as well as the screen.

    Screen writing is disable if self.silent is set.

    Args:
      message: String or List containing messages to log.
      critical: Boolean True to log as critical, otherwise logged as info.
    """
    is_list = isinstance(message, list)
    if not self.silent:
      if is_list:
        print '\n'.join(message)
      else:
        print message
    if critical:
      if is_list:
        for log in message:
          self._log.critical(log)
      else:
        self._log.critical(message)
    else:
      if is_list:
        for log in message:
          self._log.info(log)
      else:
        self._log.info(message)

  def _InitializeFullLogging(self, full_log_file):
    """Initializes full encodes log and internal list.

    This should only be called in the _ProcessArguments method.

    Args:
      full_log_file: String log to open.

    Raises:
      OptionProcessError: If the log file specified is incorrect.
    """
    try:
      self._log_full = file(full_log_file, 'a+')
    except IOError, error:
      message = 'Could not open %s! %s' % (full_log_file, error)
      self._log.error(message)
      raise OptionProcessError(message)
    self._log_full.seek(0)
    for encoded_dvd in self._log_full.readlines():
      encoded_dvd = encoded_dvd.strip()
      self._log_full_index.setdefault(encoded_dvd, True)

  def _ProcessArguements(self):
    """Processes command line arguments and sets up internal variables.

    The configuration file is automatically scanned first, to pickup logging and
    handbrake configurations for encode_dvd.

    file() is used in lue of open() for opening the full encodes log file, as a
    bug exists in mox where open() is used internally in mox.  This causes mox
    to fail horribly if open is mocked out for testing.

    Raises:
      OptionProcessError: If there is an error processing arguments.

    Returns:
      optparse.Values object containing validated options for encode_dvd to use.
    """
    options = self.parser.parse_args()[0]
    self.handbrake, full = self.config.ProcessConfig(options.config)
    self._log = logging.getLogger('EncodeDvd')
    self._InitializeFullLogging(full)

    if not options.source:
      self._log.critical('Source (%s) is None.' % options.source)
      raise OptionProcessError('Must specify source!')
    options.source = abs_path.AbsPath(options.source)
    if not options.destination and not options.list:
      self._log.critical('Destination (%s) is None, list option not used.' %
                         options.destination)
      raise OptionProcessError('Must specify a destination if not using list!')
    if options.destination:
      options.destination = abs_path.AbsPath(options.destination)
    self.mail = Mail(options.email)
    self.silent = options.quiet
    if options.hard_subtitles:
      self.handbrake.options.subtitles.SetValue(options.hard_subtitles)
      self.handbrake.options.subtitles_if_forced.SetValue(False)
      self.handbrake.options.subtitles_scan.SetValue(False)
    else:
      self.handbrake.options.subtitles.SetValue(None)
      self.handbrake.options.subtitles_if_forced.SetValue(True)
      self.handbrake.options.subtitles_scan.SetValue(True)
    if options.title:
      options.time = 0
    else:
      options.chapter_start = None
      options.chapter_end = None
      options.title = None
      if options.time < 0:
        options.time = 120
    return options

  def _GenerateValidSources(self, source_path):
    """Generates a list of valid sources found, and logs it.

    A valid source is any non-processed full path to a DVD container.  Valid
    sources are stored in self.sources.

    Args:
      source_path: String path to search for DVD containers.
    """
    self.sources = []
    self._log.info('Searching source directory %s (this may take a while) ...' %
                   source_path)
    self.dvd_containers.GenerateDvdContainers(source_path)
    self._log.info('VALID NON-PROCESSED SOURCES FOUND:')
    for source in self.dvd_containers.sources:
      if not self._log_full_index.get(source, False):
        self._log.info(source)
        self.sources.append(source)

  def _GenerateDvdTitleList(self, source_path):
    """Generates a formatted list of all the title information for given Dvd's.

    Args:
      source_path: String path to search for DVD containers.

    Raises:
      HandbrakeError: If error ocurred while using handbrake binary.
    """
    self._Log('Generating DVD list from %s (this may take a while) ...' %
              source_path)
    self.dvd_containers.GenerateDvdContainers(source_path)
    try:
      self.handbrake.Connect()
    except handbrake.Error, error:
      self._log.critical(error)
      raise HandbrakeError(error)
    for dvd in self.dvd_containers.sources:
      try:
        self.handbrake.GetDvdInformation(dvd)
      except handbrake.Error, error:
        self._log.critical(error)
        raise HandbrakeError(error)
      self._Log(['-'*80, dvd, '-'*80])
      self._Log('DVD Name: %s' % self.handbrake.dvd.name)
      for title in self.handbrake.dvd.titles:
        self._Log('%s Title %s:' % (self.handbrake.dvd.name, title.number))
        self._Log('  Video Tile Set: %s' % title.video_tile_set)
        self._Log('  Title cell start: %s' % title.cell_start)
        self._Log('  Title cell end: %s' % title.cell_end)
        self._Log('  Title cell blocks: %s' % title.cell_blocks)
        self._Log('  Horizontal Size: %s' % title.horizontal_size)
        self._Log('  Vertical Size: %s' % title.vertical_size)
        self._Log(
            '  Autocrop estimate (Top, Bottom, Left, Right): %s:%s:%s:%s' %
            (title.autocrop_top, title.autocrop_bottom,
             title.autocrop_left, title.autocrop_right))
        self._Log('  Aspect Ratio: %s' % title.aspect_ratio)
        self._Log('  Frame Rate: %s' % title.frame_rate)
        self._Log('  Chapters:')
        for chapter in title.chapters:
          self._Log('    %s' % chapter)
        self._Log('  Audio Tracks:')
        for audio in title.audio:
          self._Log('    %s' % audio)
        self._Log('  Subtitles:')
        for subtitle in title.subtitles:
          self._Log('    %s' % subtitle)

  def _ProcessCustomTitles(self, options):
    """Processes DVDs using custom title start/end options.

    Args:
      options: optparse.Values object containing options to use.

    Raises:
      HandbrakeError: If error ocurred while using handbrake binary.
    """
    self._Log('Processing custom titles ...')
    try:
      self.handbrake.Connect()
    except handbrake.Error, error:
      self._log.critical(error)
      raise HandbrakeError(error)
    for dvd in self.dvd_containers.sources:
      try:
        self.handbrake.GetDvdInformation(dvd)
      except handbrake.Error, error:
        self._log.critical(error)
        raise HandbrakeError(error)
      dvd_name = self.handbrake.dvd.name
      start = options.chapter_start
      end = options.chapter_end
      try:
        title = self.handbrake.dvd.GetTitle(options.title)
      except handbrake.dvd.TitleNotFoundError, error:
        self._Log('Title %s not found in %s' % (options.title, dvd_name), True)
        break
      if start not in title.chapters and not options.ignore:
        self._Log('Chapter start %s not found in %s - Title %s' %
                  (start, dvd_name, title.number), True)
        break
      if end not in title.chapters and not options.ignore:
        self._Log('Chapter end %s not found in %s - Title %s' %
                  (end, dvd_name, title.number), True)
        break
      self._Log('Processing %s Title %s from Chapters %s to %s ...' %
                (dvd_name, title.number, start, end))
      output_file = ('%s%s [Title %s] [Chapters %s-%s].%s' %
                     (options.destination, dvd_name, title.number, start, end,
                      self.handbrake.options.file_format.value))
      try:
        success, execution_time, title, log = (
            self.handbrake.Encode(dvd, output_file, title.number, start, end))
      except handbrake.Error, error:
        raise HandbrakeError(error)
      if not success:
        log.insert(0, 'Encoding Failed:')
        self._Log(log, True)
      else:
        message = [
            'Processed successfully in %s.' % str(execution_time).split('.')[0],
            'Encoded to: %s' % output_file]
        self._Log(message)

  def _ProcessTitles(self, options):
    """Processes DVD Titles in given directory, according to time limit.

    Args:
      options: optparse.Values object containing options to use.

    Raises:
      HandbrakeError: If error ocurred while using handbrake binary.
    """
    self.silent = True
    overall_results = []
    limit = datetime.datetime(1, 1, 1)+datetime.timedelta(seconds=options.time)
    self._Log('Processing titles (this will take a while) ...')
    try:
      self.handbrake.Connect()
    except handbrake.Error, error:
      self._log.critical(error)
      raise HandbrakeError(error)
    for dvd in self.sources:
      email_results = ['\n']
      try:
        self.handbrake.GetDvdInformation(dvd)
      except handbrake.Error, error:
        self._log.critical(error)
        raise HandbrakeError(error)
      self._Log('Encoding %s ...' % self.handbrake.dvd.name)
      try:
        results = self.handbrake.EncodeAll(dvd, options.destination, limit)
      except handbrake.Error, error:
        raise HandbrakeError(error)
      total_time = datetime.datetime(1, 1, 1)
      for success, execution_time, title, log in results:
        if success:
          total_time += execution_time
          email_results.append('Processed title %s successfully in %s.' %
                               (title, str(execution_time).split('.')[0]))
          if dvd not in self._log_full_index:
            self._log_full.write('%s\n' % dvd)
            self._log_full_index.setdefault(dvd, True)
        else:
          email_results.append('Title %s failed to encode:' % title)
          email_results.extend(log)
        email_results.append('---')
      email_results.insert(0, 'Encode results for %s. (Total time: %s)' %
                           (dvd, str(total_time.time()).split('.')[0]))
      overall_results.append('Process time: %s, Source: %s' %
                             (str(total_time.time()).split('.')[0], dvd))
      self._Log(email_results)
      self.mail.SendMail('Encode finished for %s' % dvd,
                         '\n'.join(email_results))
    self._Log('Processing %s jobs Completed.' % len(overall_results))
    if overall_results:
      self.mail.SendMail(
          'Encoding %s jobs finished.' % len(self.sources),
          '\n'.join(overall_results))

  def Execute(self):
    """Excutes encode_dvd.

    Raises:
      OptionProcessError: If arguments are invalid.
    """
    options = self._ProcessArguements()
    self._log.info('Encode DVD version %s by %s started.' %
                   (__version__, __author__))
    if options.list:
      self._GenerateDvdTitleList(options.source)
    else:
      self._GenerateValidSources(options.source)
      if options.title:
        self._ProcessCustomTitles(options)
      else:
        self._ProcessTitles(options)


def main():
  """Processes command line arguments for EncodeDvd."""
  encode_dvd = EncodeDvd()
  try:
    encode_dvd.Execute()
  except OptionProcessError, error:
    print error
    sys.exit(1)


if __name__ == '__main__':
  main()
