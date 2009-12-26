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
"""Test suite for encode_dvd CLI.

This test suite requires the use of the mox module for python.  This is located
here: http://code.google.com/p/pymox/wiki/MoxDocumentation.
"""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'

import datetime
import optparse
import os
import smtplib
import sys
import unittest
import abs_path
import dvd
import encode_dvd

try:
  import mox
except ImportError:
  raise ImportError('Python MOX must be installed to run this unittest.  See: '
                    'http://code.google.com/p/pymox/wiki/MoxDocumentation for '
                    'information on how to install this framework.')


class MockParser(object):
  """Mock parser object."""

  def __init__(self):
    self.optparse_values = optparse.Values()

  def parse_args(self):
    return [self.optparse_values]


class MockEncodeDvdOptions(object):
  """Mock OptionParser, to prevent exceptions with os.path when overriding."""

  def __init__(self):
    self.parser = MockParser()


class MockLogger(object):
  """Mock logging getLogger logger, for easy mocking."""

  def error(self, message):
    pass

  def debug(self, message):
    pass

  def critical(self, message):
    pass

  def info(self, message):
    pass


class MockOptions(object):
  """Mock options class for testing.

  Since setattr doesn't work on object classes directly, we need a subclass.
  """
  pass


class BaseEncodeDvdHelperTest(unittest.TestCase):
  """Basic setup for testing encode_dvd helper classes."""

  def setUp(self):
    self.mox = mox.Mox()
    self.real_os_path = encode_dvd.os.path
    self.real_options = encode_dvd.EncodeDvdOptions
    self.real_abs_path = encode_dvd.abs_path
    self.real_smtp = encode_dvd.smtplib
    self.real_logging = encode_dvd.logging
    encode_dvd.os.path = self.mox.CreateMock(os.path)
    encode_dvd.abs_path = self.mox.CreateMock(abs_path)
    encode_dvd.smtplib = self.mox.CreateMock(encode_dvd.smtplib)
    encode_dvd.logging = self.mox.CreateMock(encode_dvd.logging)
    self.smtp = self.mox.CreateMockAnything()
    encode_dvd.EncodeDvdOptions = MockEncodeDvdOptions

  def tearDown(self):
    self.mox.UnsetStubs()
    encode_dvd.os.path = self.real_os_path
    encode_dvd.smtplib = self.real_smtp
    encode_dvd.abs_path = self.real_abs_path
    encode_dvd.logging = self.real_logging
    encode_dvd.EncodeDvdOptions = self.real_options


class TestEncodeDvdBaseMethods(BaseEncodeDvdHelperTest):
  """Verifies the basic method in EncodeDvd work properly."""

  def setUp(self):
    BaseEncodeDvdHelperTest.setUp(self)
    self.encode = encode_dvd.EncodeDvd()
    self.config = encode_dvd.EncodeDvdConfigParser()

  def testDetermineType(self):
    """Verifies config file type determination and casting works properly."""
    self.assertEqual(self.config.DetermineType("'asdf'"), 'asdf')
    self.assertEqual(self.config.DetermineType('"asdf"'), 'asdf')
    self.assertEqual(self.config.DetermineType('False'), False)
    self.assertEqual(self.config.DetermineType('True'), True)
    self.assertEqual(self.config.DetermineType('1.0'), 1.0)
    self.assertEqual(self.config.DetermineType('1'), 1)
    self.assertEqual(self.config.DetermineType('testy'), 'testy')


class TestEncodeDvdConfigParserFindConfigFile(BaseEncodeDvdHelperTest):
  """Verifies the EncodeDvdConfigParser.FindConfigFile works properly."""

  def setUp(self):
    BaseEncodeDvdHelperTest.setUp(self)
    self.config = encode_dvd.EncodeDvdConfigParser()
    encode_dvd.abs_path.AbsPath('config').AndReturn('config')

  def testCustomLocation(self):
    """Verifies a custom location is determined correctly."""
    encode_dvd.os.path.exists('config').AndReturn(True)
    self.mox.ReplayAll()
    self.assertEqual(self.config.FindConfigFile('config'), 'config')
    self.mox.VerifyAll()

  def testFileInHomeDirectory(self):
    """Verifies a file in user's home directory is found correctly."""
    config = '~/.encode-dvd/config'
    config_full = '/home/user/.encode-dvd/config'
    encode_dvd.os.path.exists('config').AndReturn(False)
    encode_dvd.os.path.join('~', '.encode-dvd', 'config').AndReturn(config)
    encode_dvd.abs_path.AbsPath(config).AndReturn(config_full)    
    encode_dvd.os.path.exists(config_full).AndReturn(True)
    self.mox.ReplayAll()
    self.assertEqual(self.config.FindConfigFile('config'), config_full)
    self.mox.VerifyAll()

  def testEtclocation(self):
    """Verifies a config file in etc is found properly."""
    config = '/etc/encode-dvd/config'
    encode_dvd.os.path.exists('config').AndReturn(False)
    encode_dvd.os.path.join('~', '.encode-dvd', 'config').AndReturn(config)
    encode_dvd.abs_path.AbsPath(config).AndReturn(config)    
    encode_dvd.os.path.exists(config).AndReturn(False)
    encode_dvd.os.path.join('/etc', 'encode-dvd', 'config').AndReturn(config)
    encode_dvd.os.path.exists(config).AndReturn(True)
    self.mox.ReplayAll()
    self.assertEqual(self.config.FindConfigFile('config'), config)
    self.mox.VerifyAll()

  def testFileNotFound(self):
    """Verifies a configuration file not found fails properly."""
    config = '/etc/encode-dvd/config'
    encode_dvd.os.path.exists('config').AndReturn(False)
    encode_dvd.os.path.join('~', '.encode-dvd', 'config').AndReturn(config)
    encode_dvd.abs_path.AbsPath(config).AndReturn(config)    
    encode_dvd.os.path.exists(config).AndReturn(False)
    encode_dvd.os.path.join('/etc', 'encode-dvd', 'config').AndReturn(config)
    encode_dvd.os.path.exists(config).AndReturn(False)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.ConfigError, self.config.FindConfigFile,
                      'config')
    self.mox.VerifyAll()


class TestEncodeDvdConfigProcessConfig(BaseEncodeDvdHelperTest):
  """Verifies EncodeDvdConfigProcessConfig works."""

  def setUp(self):
    self.mox = mox.Mox()
    self.config = encode_dvd.EncodeDvdConfigParser()
    self.file = 'file'

  def tearDown(self):
    self.mox.UnsetStubs()

  def testActualFile(self):
    """Verifies a test configuration file works properly."""
    hb, log = self.config.ProcessConfig(
        './testdata/config_test_data/encode_dvd.config')
    self.assertEqual(hb.options.file_format.value, 'mp4')
    self.assertEqual(hb.options.file_markers.value, True)
    self.assertEqual(hb.options.video_encoder.value, 'x264')
    self.assertEqual(hb.options.video_x264_opts.value,
                     'ref=1:me=umh:me-range=32:subme=7:analyse=all:filter=0,0:'
                     'no-fast-pskip=1:cabac=1:bframes=16:direct=auto:weightb=1:'
                     'subq=7:level=4.1')
    self.assertEqual(hb.options.video_two_pass.value, True)
    self.assertEqual(hb.options.video_x264_turbo_first_pass.value, True)
    self.assertEqual(hb.options.video_bitrate.value, 1800)
    self.assertEqual(hb.options.audio_encoder.value, 'faac')
    self.assertEqual(hb.options.audio_bitrate.value, '384')
    self.assertEqual(hb.options.audio_mixdown.value, '6ch')
    self.assertEqual(hb.options.audio_dynamic_range_compression.value, '1.0')
    self.assertEqual(hb.options.strict_anamorphic.value, True)
    self.assertEqual(hb.options.filter_decomb.value, 'slower')
    self.assertEqual(hb.options.subtitles_scan.value, True)
    self.assertEqual(hb.options.subtitles_if_forced.value, True)
    self.assertEqual(hb.options.subtitles_native_language.value, 'eng')
    self.assertEqual(log, '/var/log/encode-dvd/full_encodes.log')

  def testBadFile(self):
    """Verifies a file read error fails properly."""
    self.mox.StubOutWithMock(self.config, 'FindConfigFile')
    self.config.FindConfigFile(self.file).AndReturn(self.file)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.ConfigError, self.config.ProcessConfig,
                      self.file)
    self.mox.VerifyAll()

  def testBadSections(self):
    """Verifies a bad config file sections fails properly."""
    self.assertRaises(
        encode_dvd.ConfigError, self.config.ProcessConfig,
        './testdata/config_test_data/encode_dvd_bad_handbrake_section.config')
    self.assertRaises(
        encode_dvd.ConfigError, self.config.ProcessConfig,
        './testdata/config_test_data/encode_dvd_bad_logging_section.config')

  def testBadHandbrakeKey(self):
    """Verifies an invalid handbrake key fails properly."""
    self.assertRaises(encode_dvd.ConfigError, self.config.ProcessConfig,
                      './testdata/config_test_data/encode_dvd_bad_key.config')

  def testBadLoggingKey(self):
    """Verifies an invalid logging key fails properly."""
    self.assertRaises(encode_dvd.ConfigError, self.config.ProcessConfig,
                      './testdata/config_test_data/encode_dvd_bad_key.config')


class TestDvdContainerGenerator(BaseEncodeDvdHelperTest):
  """Verifies EncodeDvdDvdContainerGenerator works properly."""

  def setUp(self):
    BaseEncodeDvdHelperTest.setUp(self)
    self.generator = encode_dvd.DvdContainerGenerator()

  def testDvdFilterNoMatch(self):
    """Verifies the DVD filter with no match works properly."""
    encode_dvd.os.path.basename('video_ts').AndReturn('')
    self.mox.ReplayAll()
    self.generator._DvdFilter([], 'video_ts', '')
    self.mox.VerifyAll()

  def testDvdFilterMatch(self):
    """Verifies the DVD filter with match works properly."""
    test_arg = []
    encode_dvd.os.path.basename('/tmp/video_ts').AndReturn('video_ts')
    encode_dvd.os.path.dirname('/tmp/video_ts').AndReturn('/tmp/')
    encode_dvd.abs_path.AbsPath('/tmp/').AndReturn('/tmp/')
    self.mox.ReplayAll()
    self.generator._DvdFilter(test_arg, '/tmp/video_ts', '')
    self.assertEqual(test_arg, ['/tmp/'])
    self.mox.VerifyAll()

  def testGenerateDvdContainers(self):
    """Verifies GenerateDvdContainers works properly."""
    encode_dvd.os.path.walk(
        '/tmp/',
        mox.IsA(encode_dvd.DvdContainerGenerator._DvdFilter),
        mox.IsA(list))
    self.mox.ReplayAll()
    self.generator.GenerateDvdContainers('/tmp/')
    self.mox.VerifyAll()

  def testRemoveDuplicates(self):
    """Verifies duplicate DVD containers are removed properly."""
    self.generator.sources = ['ab', 'ac', 'ad']
    new_sources = ['ab', 'ac\n']
    self.generator.RemoveDuplicates(new_sources)
    self.assertEqual(self.generator.sources, ['ad'])


class TestMail(BaseEncodeDvdHelperTest):
  """Verifies the mail class works properly."""

  def setUp(self):
    BaseEncodeDvdHelperTest.setUp(self)
    self.mail = encode_dvd.Mail('a@b.com')
    encode_dvd.smtplib.SMTP('localhost').AndReturn(self.smtp)

  def testSendMail(self):
    """Verifies sending an e-mail works properly."""
    self.smtp.sendmail('a@b.com', 'a@b.com', 'Subject: subject\n\nbody')
    self.smtp.close()
    self.mox.ReplayAll()
    self.mail.SendMail('subject', 'body')
    self.mox.VerifyAll()

  def testSendMailFail(self):
    """Verifies sending an e-mail fails properly."""
    self.smtp.sendmail(
        'a@b.com', 'a@b.com', 'Subject: subject\n\nbody').AndRaise(
            smtplib.socket.error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.EmailError, self.mail.SendMail,
                      'subject', 'body')
    self.mox.VerifyAll()

  def testNoSendMail(self):
    """Verifies mail is NOT sent if no e-mail address is specified."""
    encode_dvd.smtplib = self.real_smtp
    self.mox = mox.Mox()
    self.mail = encode_dvd.Mail()
    self.mox.ReplayAll()
    self.mail.SendMail('subject', 'body')
    self.mox.VerifyAll()


class EncodeDvdProcessArguementsTest(unittest.TestCase):
  """Basic setup for testing encode_dvd options."""

  def setUp(self):
    self.mox = mox.Mox()
    self.options = MockOptions()
    setattr(self.options, 'source', None)
    setattr(self.options, 'destination', None)
    setattr(self.options, 'email', None)
    setattr(self.options, 'time', 120)
    setattr(self.options, 'hard_subtitles', False)
    setattr(self.options, 'force_subtitles', False)
    setattr(self.options, 'chapter_start', None)
    setattr(self.options, 'chapter_end', None)
    setattr(self.options, 'title', None)
    setattr(self.options, 'quiet', False)
    setattr(self.options, 'config', 'encode_dvd.config')
    setattr(self.options, 'list', False)
    self.real_logging = encode_dvd.logging
    self.real_abs_path = encode_dvd.abs_path
    self.real_modules = sys.modules['__builtin__'].file
    encode_dvd.logging = self.mox.CreateMock(encode_dvd.logging)
    encode_dvd.abs_path = self.mox.CreateMock(encode_dvd.abs_path)
    sys.modules['__builtin__'].file = self.mox.CreateMockAnything()

    # Create EncodeDvd object without calling constructor
    # This is needed to test encode.config without reading a source file.
    self.encode = encode_dvd.EncodeDvd.__new__(encode_dvd.EncodeDvd)
    self.encode._log_full = self.mox.CreateMockAnything()
    self.encode.parser = MockParser()
    self.encode.config = self.mox.CreateMock(encode_dvd.EncodeDvdConfigParser)
    self.encode.dvd_containers = self.mox.CreateMock(
        encode_dvd.DvdContainerGenerator)
    self.mox.StubOutWithMock(self.encode, '__del__')
    self.encode.config.ProcessConfig('encode_dvd.config').AndReturn(
        (encode_dvd.handbrake.HandBrake(), 'file'))
    encode_dvd.logging.getLogger('EncodeDvd').AndReturn(MockLogger())

  def tearDown(self):
    self.mox.UnsetStubs()
    encode_dvd.logging = self.real_logging
    encode_dvd.abs_path = self.real_abs_path
    sys.modules['__builtin__'].file = self.real_modules

  def GenericProcessArguementsSetup(self, error_file=False, source=True,
                                    destination=True):
    """Generic test setup for ProcessArguements.

    Args:
      error_file: Boolean True to raise a IOError when opening full log.
      source: Boolean True to mock abs_path.AbsPath method for source.
      destination: Boolean True to mock abs_path.AbsPath method for destination.
    """
    self.encode.parser.optparse_values = self.options
    if error_file:
      sys.modules['__builtin__'].file('file', 'a+').AndRaise(IOError)
    else:
      sys.modules['__builtin__'].file('file', 'a+').AndReturn(None)
    if source:
      encode_dvd.abs_path.AbsPath(True).AndReturn(True)
    if destination:
      encode_dvd.abs_path.AbsPath(True).AndReturn(True)

  def testInvalidLogCompletedFile(self):
    """Verifies an invalid log full file is handled properly."""
    self.GenericProcessArguementsSetup(error_file=True, source=False,
                                       destination=False)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.OptionProcessError,
                      self.encode._ProcessArguements)
    self.mox.VerifyAll()

  def testBadSource(self):
    """Verifies invalid source files are handled properly."""
    self.GenericProcessArguementsSetup(source=False, destination=False)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.OptionProcessError,
                      self.encode._ProcessArguements)
    self.mox.VerifyAll()

  def testBadDestination(self):
    """Verifies invalid destination files are handled properly."""
    setattr(self.options, 'source', True)
    self.GenericProcessArguementsSetup(source=True, destination=False)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.OptionProcessError,
                      self.encode._ProcessArguements)
    self.mox.VerifyAll()

  def testNoDestinationList(self):
    """Verifies listing DVD information works properly."""
    setattr(self.options, 'source', True)
    setattr(self.options, 'list', True)
    self.GenericProcessArguementsSetup(source=True, destination=False)
    self.mox.ReplayAll()
    self.encode._ProcessArguements()
    self.mox.VerifyAll()

  def testMailOptions(self):
    """Verifies a mail option is set correctly."""
    setattr(self.options, 'source', True)
    setattr(self.options, 'destination', True)
    setattr(self.options, 'email', 'a@b.com')
    self.GenericProcessArguementsSetup()
    self.mox.ReplayAll()
    self.encode._ProcessArguements()
    self.assertEqual(self.encode.mail.address, 'a@b.com')
    self.mox.VerifyAll()

  def testHardSubtitles(self):
    """Verifies hard subtitles are enforced correctly."""
    setattr(self.options, 'source', True)
    setattr(self.options, 'destination', True)
    setattr(self.options, 'hard_subtitles', 1)
    setattr(self.options, 'force_subtitles', True)
    self.GenericProcessArguementsSetup()
    self.mox.ReplayAll()
    options = self.encode._ProcessArguements()
    self.assertEqual(self.encode.handbrake.options.subtitles.value, 1)
    self.assertEqual(self.encode.handbrake.options.subtitles_scan.value, False)
    self.assertEqual(self.encode.handbrake.options.subtitles_if_forced.value,
                     False)
    self.mox.VerifyAll()

  def testForceSubtitles(self):
    """Verifies forced subtitles are enforced correctly."""
    setattr(self.options, 'source', True)
    setattr(self.options, 'destination', True)
    setattr(self.options, 'hard_subtitles', None)
    setattr(self.options, 'force_subtitles', True)
    self.GenericProcessArguementsSetup()
    self.mox.ReplayAll()
    options = self.encode._ProcessArguements()
    self.assertEqual(self.encode.handbrake.options.subtitles.value, None)
    self.assertEqual(self.encode.handbrake.options.subtitles_scan.value, True)
    self.assertEqual(self.encode.handbrake.options.subtitles_if_forced.value,
                     True)
    self.mox.VerifyAll()

  def testTitle(self):
    """Verifies a title option sets options properly."""
    setattr(self.options, 'source', True)
    setattr(self.options, 'destination', True)
    setattr(self.options, 'title', 3)
    self.GenericProcessArguementsSetup()
    self.mox.ReplayAll()
    options = self.encode._ProcessArguements()
    self.assertEqual(options.title, 3)
    self.assertEqual(options.time, 0)
    self.mox.VerifyAll()

  def testNoTitle(self):
    """Verifies no title option specified sets options properly."""
    setattr(self.options, 'source', True)
    setattr(self.options, 'destination', True)
    setattr(self.options, 'time', -123123)
    self.GenericProcessArguementsSetup()
    self.mox.ReplayAll()
    options = self.encode._ProcessArguements()
    self.assertEqual(options.time, 120)
    self.assertEqual(options.chapter_start, None)
    self.assertEqual(options.chapter_end, None)
    self.assertEqual(options.title, None)
    self.mox.VerifyAll()


class EncodeDvdTest(unittest.TestCase):
  """Basic setup for testing encode_dvd methods."""

  def setUp(self):
    self.mox = mox.Mox()
    self.options = MockOptions()
    setattr(self.options, 'chapter_start', 1)
    setattr(self.options, 'chapter_end', 2)
    setattr(self.options, 'title', 1)
    setattr(self.options, 'destination', '/tmp/')
    setattr(self.options, 'time', 120)
    setattr(self.options, 'ignore', False)
    self.encode = encode_dvd.EncodeDvd()
    self.encode.silent = True
    self.encode._log = MockLogger()
    self.encode._log_full = self.mox.CreateMockAnything()
    self.encode.parser = MockParser()
    self.encode.config = self.mox.CreateMock(encode_dvd.EncodeDvdConfigParser)
    self.mox.StubOutWithMock(self.encode, 'dvd_containers')
    self.mox.StubOutWithMock(self.encode, '__del__')
    self.mox.StubOutWithMock(self.encode, 'handbrake')
    self.encode.mail = encode_dvd.Mail()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testGenerateSources(self):
    """Verifies a source list is generated properly."""
    self.encode.dvd_containers.sources = ['af']
    self.encode.dvd_containers.GenerateDvdContainers('path')
    self.encode._log_full.seek(0).AndReturn(True)
    self.encode._log_full.readlines().AndReturn(['ab', 'ac'])
    self.encode.dvd_containers.RemoveDuplicates(['ab', 'ac'])
    self.mox.ReplayAll()
    self.encode._GenerateSources('path')
    self.mox.VerifyAll()

  def testLog(self):
    """Verifies the _Log method works properly."""
    self.encode.silent = True
    self.encode._Log('you should not see this', True)
    self.encode._Log('you should not see this')

  def testGenerateDvdTitleList(self):
    """Verifies _GenerateDvdTitleList works properly."""
    self.encode.dvd_containers.sources = ['dvd_path']
    self.encode.handbrake.dvd = dvd.Dvd('test', [dvd.Title()])
    self.encode.dvd_containers.GenerateDvdContainers('path')
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('dvd_path')
    self.mox.ReplayAll()
    self.encode._GenerateDvdTitleList('path')
    self.mox.VerifyAll()

  def testGenerateDvdTitleListBadConnect(self):
    """Verifies _GenerateDvdTitleList fails properly on bad connect."""
    self.encode.dvd_containers.GenerateDvdContainers('path')
    self.encode.handbrake.Connect().AndRaise(encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._GenerateDvdTitleList,
                      'path')
    self.mox.VerifyAll()

  def testGenerateDvdTitleListBadDvdInformation(self):
    """Verifies _GenerateDvdTitleList fails properly on bad dvd information."""
    self.encode.dvd_containers.sources = ['dvd_path']
    self.encode.dvd_containers.GenerateDvdContainers('path')
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('dvd_path').AndRaise(
        encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._GenerateDvdTitleList,
                      'path')
    self.mox.VerifyAll()

  def testProcessCustomTitles(self):
    """Verifies valid custom titles are processed correctly."""
    title = dvd.Title()
    title.AddChapter(dvd.Chapter(number=1), dvd.Chapter(number=2))
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD', [title])
    self.encode.handbrake.options = (
        encode_dvd.handbrake.handbrake_options.Options())
    self.encode.handbrake.options.file_format.value = 'mp4'
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.encode.handbrake.Encode(
        '/my', '/tmp/DVD [Title 1] [Chapters 1-2].mp4', 1, 1, 2).AndReturn(
            (True, datetime.timedelta(0, 10, 464765), 'DVD', []))
    self.mox.ReplayAll()
    self.encode._ProcessCustomTitles(self.options)
    self.mox.VerifyAll()

  def testProcessCustomTitlesWithIgnore(self):
    """Verifies valid custom titles are processed correctly with ignore."""
    self.options.ignore = True
    self.options.chapter_start = 3
    self.options.chapter_end = 4
    title = dvd.Title()
    title.AddChapter(dvd.Chapter(number=1), dvd.Chapter(number=2))
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD', [title])
    self.encode.handbrake.options = (
        encode_dvd.handbrake.handbrake_options.Options())
    self.encode.handbrake.options.file_format.value = 'mp4'
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.encode.handbrake.Encode(
        '/my', '/tmp/DVD [Title 1] [Chapters 3-4].mp4', 1, 3, 4).AndReturn(
            (True, datetime.timedelta(0, 10, 464765), 'DVD', []))
    self.mox.ReplayAll()
    self.encode._ProcessCustomTitles(self.options)
    self.mox.VerifyAll()

  def testProcessCustomTitlesBadConnect(self):
    """Verifies _ProcessCustomTitles fails properly on bad connect."""
    self.encode.handbrake.Connect().AndRaise(encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._ProcessCustomTitles,
                      self.options)
    self.mox.VerifyAll()

  def testProcessCustomTitlesBadDvdInformation(self):
    """Verifies _ProcessCustomTitles fails properly on bad dvd information."""
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD')
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my').AndRaise(
        encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._ProcessCustomTitles,
                      self.options)
    self.mox.VerifyAll()

  def testProcessCustomTitlesBadTitle(self):
    """Verifies a bad title fails properly."""
    setattr(self.options, 'title', 3)
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD')
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.mox.ReplayAll()
    self.encode._ProcessCustomTitles(self.options)
    self.mox.VerifyAll()

  def testProcessCustomTitlesBadStart(self):
    """Verifies a bad title chapter start fails properly."""
    setattr(self.options, 'chapter_start', 5)
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD')
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.mox.ReplayAll()
    self.encode._ProcessCustomTitles(self.options)
    self.mox.VerifyAll()

  def testProcessCustomTitlesBadEnd(self):
    """Verifies a bad title chapter end fails properly."""
    setattr(self.options, 'chapter_end', 5)
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD')
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.mox.ReplayAll()
    self.encode._ProcessCustomTitles(self.options)
    self.mox.VerifyAll()

  def testProcessCustomTitlesBadEncode(self):
    """Verifies a bad title encode fails properly."""
    title = dvd.Title()
    title.AddChapter(dvd.Chapter(number=1), dvd.Chapter(number=2))
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD', [title])
    self.encode.handbrake.options = (
        encode_dvd.handbrake.handbrake_options.Options())
    self.encode.handbrake.options.file_format.value = 'mp4'
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.encode.handbrake.Encode(
        '/my', '/tmp/DVD [Title 1] [Chapters 1-2].mp4', 1, 1, 2).AndRaise(
            encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._ProcessCustomTitles,
                      self.options)
    self.mox.VerifyAll()

  def testProcessTitles(self):
    """Verifies _ProcessTitles works properly."""
    title = dvd.Title()
    title.AddChapter(dvd.Chapter(number=1), dvd.Chapter(number=2))
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD', [title])
    self.encode.handbrake.options = (
        encode_dvd.handbrake.handbrake_options.Options())
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.encode.handbrake.EncodeAll(
        '/my', '/tmp/', datetime.datetime(1, 1, 1, 0, 2, 0)).AndReturn(
            [(True, datetime.timedelta(0, 10, 464765), 'DVD', [])])
    self.encode._log_full.write('/my\n')
    self.mox.ReplayAll()
    self.encode._ProcessTitles(self.options)
    self.mox.VerifyAll()

  def testProcessTitlesBadConnect(self):
    """Verifies _ProcessTitles fails properly with bad connect."""
    self.encode.handbrake.Connect().AndRaise(encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._ProcessTitles, self.options)
    self.mox.VerifyAll()

  def testProcessTitlesBadDvdInformation(self):
    """Verifies _ProcessTitles fails properly with bad DVD Information."""
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my').AndRaise(
        encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._ProcessTitles, self.options)
    self.mox.VerifyAll()

  def testProcessTitlesBadEncode(self):
    """Verifies _ProcessTitles fails properly for bad encode."""
    title = dvd.Title()
    title.AddChapter(dvd.Chapter(number=1), dvd.Chapter(number=2))
    self.encode.dvd_containers.sources = ['/my']
    self.encode.handbrake.dvd = dvd.Dvd('DVD', [title])
    self.encode.handbrake.options = (
        encode_dvd.handbrake.handbrake_options.Options())
    self.encode.handbrake.Connect()
    self.encode.handbrake.GetDvdInformation('/my')
    self.encode.handbrake.EncodeAll(
        '/my', '/tmp/', datetime.datetime(1, 1, 1, 0, 2, 0)).AndRaise(
            encode_dvd.handbrake.Error)
    self.mox.ReplayAll()
    self.assertRaises(encode_dvd.HandbrakeError,
                      self.encode._ProcessTitles, self.options)
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()
