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
"""Test suite for handbrake interface.

This test suite requires the use of the mox module for python.  This is located
here: http://code.google.com/p/pymox/wiki/MoxDocumentation.
"""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'

import datetime
import os
import subprocess
import tempfile
import unittest
import abs_path
import dvd
import handbrake
import options

try:
  import mox
except ImportError:
  raise ImportError('Python MOX must be installed to run this unittest.  See: '
                    'http://code.google.com/p/pymox/wiki/MoxDocumentation for '
                    'information on how to install this framework.')


class BaseHandBrakeTest(unittest.TestCase):
  """Base setup for Handbrake testing."""

  def setUp(self):
    self.mox = mox.Mox()
    self.real_os_path = handbrake.os.path
    self.real_subprocess = handbrake.subprocess
    self.real_tempfile = handbrake.tempfile
    self.real_abs_path = handbrake.abs_path

  def tearDown(self):
    self.mox.UnsetStubs()
    handbrake.os.path = self.real_os_path
    handbrake.subprocess = self.real_subprocess
    handbrake.tempfile = self.real_tempfile
    handbrake.abs_path = self.real_abs_path


class TestHandBrakeBasic(BaseHandBrakeTest):
  """Verifies basic HandBrake methods work properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    self.interface = handbrake.HandBrake()

  def testConnect(self):
    """Verifies Connect works properly."""
    binary = 'HandBrakeCLI'
    self.mox.StubOutWithMock(self.interface, '_FindBinaryLocation')
    self.mox.StubOutWithMock(self.interface, '_CheckVersion')
    self.interface._FindBinaryLocation(binary).AndReturn(binary)
    self.interface._CheckVersion()

    self.mox.ReplayAll()
    self.interface.Connect(binary)
    self.mox.VerifyAll()
    self.assertEquals(self.interface._location, binary)

  def testValidateOptions(self):
    """Verifies options are validated properly."""
    self.assertFalse(self.interface._ValidateOptions([1, 2, 3]))
    self.assertFalse(self.interface._ValidateOptions(None))
    self.assertTrue(
        self.interface._ValidateOptions(self.interface.options.all))

  def testWriteLog(self):
    """Verifies a log file is written correctly."""
    log = ['log\n',
           '\rEncoding: task 2 of 3, 99.74 %\rEncoding: task 2 of 3 ...\n',
           'log\n']
    self.interface._WriteLog(log)
    self.assertEqual(self.interface._log, ['log\n', 'log\n'])

  def testSetChapterOptions(self):
    """Verifies valid chapter options are set correctly."""
    self.interface._SetChapterOptions(None, None)
    self.assertEqual(self.interface.options.file_chapters.value,
                     self.interface.options.file_chapters.default)
    self.interface._SetChapterOptions(0, 1)
    self.assertEqual(self.interface.options.file_chapters.value, '0-1')
    self.interface._SetChapterOptions(1, 1)
    self.assertEqual(self.interface.options.file_chapters.value, '1-1')

  def testSetChapterOptionsBad(self):
    """Verifies invalid options are handled properly."""
    self.assertRaises(handbrake.EncodeError, self.interface._SetChapterOptions,
                      1, 0)


class TestHandBrakeFindBinaryLocation(BaseHandBrakeTest):
  """Verifies the HandBrake._FindBinaryLocation method works properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    handbrake.os.path = self.mox.CreateMock(os.path)
    self.interface = handbrake.HandBrake()
    self.binary = 'HandBrakeCLI'
    self.usr_binary = '/usr/bin/HandBrakeCLI'
    self.usr_bin_binary = '/usr/local/bin/HandBrakeCLI'
    self.bin_binary = '/bin/HandBrakeCLI'
    self.opt_binary = '/opt/bin/HandBrakeCLI'

  def testFindBinaryLocation(self):
    """Verifies _FindBinaryLocation works properly."""
    handbrake.os.path.exists(self.binary).AndReturn(True)
    handbrake.os.path.exists(self.binary).AndReturn(False)
    handbrake.os.path.join('/usr/bin', self.binary).AndReturn(self.usr_binary)
    handbrake.os.path.exists(self.usr_binary).AndReturn(True)
    self.mox.ReplayAll()
    self.assertEquals(self.interface._FindBinaryLocation(self.binary),
                      self.binary)
    self.assertEquals(self.interface._FindBinaryLocation(self.binary),
                      self.usr_binary)
    self.mox.VerifyAll()

  def testFindBinaryLocationFail(self):
    """Verifies _FindBinaryLocation fails properly."""
    handbrake.os.path.exists('asdf').AndReturn(False)
    handbrake.os.path.join('/usr/bin', self.binary).AndReturn(self.usr_binary)
    handbrake.os.path.exists('/usr/bin/HandBrakeCLI').AndReturn(False)
    handbrake.os.path.join('/usr/local/bin', self.binary).AndReturn(
        self.usr_bin_binary)
    handbrake.os.path.exists('/usr/local/bin/HandBrakeCLI').AndReturn(False)
    handbrake.os.path.join('/bin', self.binary).AndReturn(self.bin_binary)
    handbrake.os.path.exists('/bin/HandBrakeCLI').AndReturn(False)
    handbrake.os.path.join('/opt/bin', self.binary).AndReturn(self.opt_binary)
    handbrake.os.path.exists('/opt/bin/HandBrakeCLI').AndReturn(False)
    self.mox.ReplayAll()
    self.assertRaises(handbrake.BinaryNotFoundError,
                      self.interface._FindBinaryLocation, 'asdf')
    self.mox.VerifyAll()


class TestHandBrakeCheckVersion(BaseHandBrakeTest):
  """Verifies the HandBrake._CheckVersion method works properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    self.interface = handbrake.HandBrake()
    self.mox.StubOutWithMock(self.interface, '_Execute')
    self.interface._Execute(mox.IsA(list))

  def testCheckVersion(self):
    """Verifies _CheckVersion works properly."""
    self.interface._log = (
        ['HandBrake 0.9.3 (2008112300) - http://handbrake.fr/\n',
         'Your version of HandBrake is up to date.\n'])
    self.mox.ReplayAll()
    self.interface._CheckVersion()
    self.mox.VerifyAll()

  def testInvalidCheckVersion(self):
    """Verifies an invalid version for _CheckVersion is caught correctly."""
    self.interface._Execute(mox.IsA(list))
    self.interface._Execute(mox.IsA(list))
    self.interface._log = (
        ['HandBrake 0.9.3 (2008112301) - http://handbrake.fr/\n',
         'Your version of HandBrake is up to date.\n'])
    self.mox.ReplayAll()
    self.assertRaises(handbrake.VersionError, self.interface._CheckVersion)
    self.interface._log = []
    self.assertRaises(handbrake.VersionError, self.interface._CheckVersion)
    self.interface._log = ['asdf']
    self.assertRaises(handbrake.VersionError, self.interface._CheckVersion)
    self.mox.VerifyAll()


class TestHandBrakeExecute(BaseHandBrakeTest):
  """Verifies the HandBrake._Execute method works properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    self.subprocess = self.mox.CreateMock(subprocess)
    self.tempfile = self.mox.CreateMockAnything()
    self.interface = handbrake.HandBrake()

  def GenericExecuteTestSetup(self, results=0, raise_exception=False):
    """Generic test setup for _Execute.

    Args:
      results: Integer subprocess execute results.
      raise_exception: Boolean True to raise a subprocess exception.  Overrides
        results values.
    """
    if raise_exception:
      self.subprocess.call(mox.IsA(list),
                           stdout=mox.IgnoreArg(),
                           stderr=mox.IgnoreArg(),
                           shell=False).AndRaise(OSError)
    else:
      self.subprocess.call(mox.IsA(list),
                           stdout=mox.IgnoreArg(),
                           stderr=mox.IgnoreArg(),
                           shell=False).AndReturn(results)
    handbrake.subprocess = self.subprocess
    handbrake.tempfile = self.mox.CreateMock(tempfile)
    self.interface = handbrake.HandBrake()
    self.mox.StubOutWithMock(self.interface, '_CheckVersion')
    self.interface._CheckVersion()
    handbrake.tempfile.TemporaryFile().AndReturn(self.tempfile)

  def GenericTempFileSetup(self):
    """Generic test setup for faking tempfile usage."""
    self.tempfile.seek(0)
    self.tempfile.readlines().AndReturn('')
    self.tempfile.close()

  def testExecute(self):
    """Verifies the _Execute method works properly."""
    self.GenericExecuteTestSetup(results=0)
    self.GenericTempFileSetup()
    self.mox.ReplayAll()
    self.interface.Connect()
    self.interface._Execute(self.interface.options.all)
    self.mox.VerifyAll()

  def testExecuteException(self):
    """Verifies the _Execute method catches OSError correctly."""
    self.GenericExecuteTestSetup(raise_exception=True)
    self.mox.ReplayAll()
    self.interface.Connect()
    self.assertRaises(handbrake.ExecuteError, self.interface._Execute,
                      self.interface.options.all)
    self.mox.VerifyAll()

  def testExecuteFailure(self):
    """Verifies the _Execute method fails correctly."""
    self.GenericExecuteTestSetup(results=1)
    self.GenericTempFileSetup()
    self.mox.ReplayAll()
    self.interface.Connect()
    self.assertRaises(handbrake.ExecuteError, self.interface._Execute,
                      self.interface.options.all)
    self.mox.VerifyAll()

  def testExecuteNoOptions(self):
    """Verifies no options passed to _Execute fails properly."""
    self.assertRaises(handbrake.ExecuteError, self.interface._Execute, None)


class TestHandBrakeGetDvdInformation(BaseHandBrakeTest):
  """Verifies the HandBrake.GetDvdInformation method works properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    handbrake.abs_path = self.mox.CreateMock(abs_path)
    self.interface = handbrake.HandBrake()
    self.file = '/my/file'
    self.executeoptions = [mox.IsA(options.StringOption),
                           mox.IsA(options.RangeOption)]

  def testGetDvdInformation(self):
    """Verifies GetDvdInformation works properly."""
    self.mox.StubOutWithMock(self.interface, '_Execute')
    self.mox.StubOutWithMock(self.interface, 'dvd')
    handbrake.abs_path.AbsPath(self.file).AndReturn(self.file)
    self.interface._Execute(self.executeoptions)
    self.interface.dvd.ProcessHandbrakeAnalysis([])
    self.mox.ReplayAll()
    self.interface.GetDvdInformation(self.file)
    self.mox.VerifyAll()


class TestHandBrakeSetEncodeOptions(BaseHandBrakeTest):
  """Verifies the HandBrake._SetEncodeOptions method works properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    handbrake.os.path = self.mox.CreateMock(os.path)
    self.interface = handbrake.HandBrake()
    self.file = 'file'
    self.title = 1
    self.title_longest = 'longest'
    handbrake.abs_path = self.mox.CreateMock(abs_path)
    handbrake.abs_path.AbsPath(self.file).AndReturn(self.file)
    handbrake.abs_path.AbsPath(self.file).AndReturn(self.file)

  def testSetEncodeOptionsGoodWithTitle(self):
    """Verifies _SetEncodeOptions works with numeric title properly."""
    handbrake.os.path.exists(self.file).AndReturn(True)
    handbrake.os.path.dirname(self.file).AndReturn(self.file)
    handbrake.os.path.exists(self.file).AndReturn(True)
    self.mox.ReplayAll()
    self.interface._SetEncodeOptions(self.file, self.file, self.title)
    self.mox.VerifyAll()
    self.assertEqual(self.interface.options.file_input.value, self.file)
    self.assertEqual(self.interface.options.file_output.value, self.file)
    self.assertEqual(self.interface.options.file_title.value, self.title)
    self.assertEqual(self.interface.options.file_longest_title.value, False)

  def testSetEncodeOptionsGoodWithLongest(self):
    """Verifies _SetEncodeOptions works with longest title properly."""
    handbrake.os.path.exists(self.file).AndReturn(True)
    handbrake.os.path.dirname(self.file).AndReturn(self.file)
    handbrake.os.path.exists(self.file).AndReturn(True)
    self.mox.ReplayAll()
    self.interface._SetEncodeOptions(self.file, self.file, self.title_longest)
    self.mox.VerifyAll()
    self.assertEqual(self.interface.options.file_input.value, self.file)
    self.assertEqual(self.interface.options.file_output.value, self.file)
    self.assertEqual(self.interface.options.file_title.value,
                     self.interface.options.file_title.default)
    self.assertEqual(self.interface.options.file_chapters.value,
                     self.interface.options.file_chapters.default)
    self.assertEqual(self.interface.options.file_longest_title.value, True)

  def testBadSetEncodeOptions(self):
    """Verifies bad _SetEncodeOptions fail properly."""
    handbrake.os.path.exists(self.file).AndReturn(False)
    handbrake.abs_path.AbsPath(self.file).AndReturn(self.file)
    handbrake.abs_path.AbsPath(self.file).AndReturn(self.file)
    handbrake.os.path.exists(self.file).AndReturn(True)
    handbrake.os.path.dirname(self.file).AndReturn(self.file)
    handbrake.os.path.exists(self.file).AndReturn(False)
    self.mox.ReplayAll()
    self.assertRaises(handbrake.EncodeError, self.interface._SetEncodeOptions,
                      self.file, self.file, self.title)
    self.assertRaises(handbrake.EncodeError, self.interface._SetEncodeOptions,
                      self.file, self.file, self.title)
    self.mox.VerifyAll()


class TestHandBrakeEncode(BaseHandBrakeTest):
  """Verifies the HandBrake.Encode method works properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    handbrake.os.path = self.mox.CreateMock(os.path)
    handbrake.abs_path = self.mox.CreateMock(handbrake.abs_path)
    self.interface = handbrake.HandBrake()
    self.mox.StubOutWithMock(self.interface, '_SetChapterOptions')
    self.mox.StubOutWithMock(self.interface, '_SetEncodeOptions')
    self.mox.StubOutWithMock(self.interface, '_Execute')
    self.file = 'file'

  def testEncode(self):
    """Verifies Encode works properly."""
    success = True
    title = 1
    log = []
    self.interface._SetChapterOptions(None, None)
    self.interface._SetEncodeOptions(self.file, self.file, 1)
    handbrake.abs_path.AbsPath(self.file).AndReturn(self.file)
    handbrake.os.path.exists(self.file).AndReturn(False)
    self.interface._Execute(mox.IgnoreArg())
    self.mox.ReplayAll()
    test_result = self.interface.Encode(self.file, self.file, 1)
    self.assertEqual(test_result[0], success)
    self.assertEqual(test_result[2], title)
    self.assertEqual(test_result[3], log)
    self.mox.VerifyAll()

  def testEncodeExistingFile(self):
    """Verifies Encode fails if there is an existing output file."""
    results = (False, 0, 'longest',
               ['Title (longest) Will not overwrite output file: file.'])
    self.interface._SetChapterOptions(None, None)
    self.interface._SetEncodeOptions(self.file, self.file, 'longest')
    handbrake.abs_path.AbsPath(self.file).AndReturn(self.file)
    handbrake.os.path.exists(self.file).AndReturn(True)
    self.mox.ReplayAll()
    self.assertEqual(self.interface.Encode(self.file, self.file, 'longest'),
                     results)
    self.mox.VerifyAll()


class TestHandBrakeEncodeAll(BaseHandBrakeTest):
  """Verifies the HandBrake.EncodeAll method works properly."""

  def setUp(self):
    BaseHandBrakeTest.setUp(self)
    handbrake.os.path = self.mox.CreateMock(os.path)
    handbrake.abs_path = self.mox.CreateMock(handbrake.abs_path)
    self.interface = handbrake.HandBrake()
    self.interface.options.file_format.SetValue('mp4')
    self.mox.StubOutWithMock(self.interface, 'Encode')
    self.mox.StubOutWithMock(self.interface, 'GetDvdInformation')
    self.title1 = dvd.Title()
    self.title2 = dvd.Title(duration='01:53:27', number=2)
    self.input = '/my/movie'
    self.output = '/my/output/dir/'

  def testEncodeShortTitle(self):
    """Verifies EncodeAll works with a single short title properly."""
    results = [(False, datetime.timedelta(0), 1,
                ['Skipping Title 1 (00:00:00), shorter than 00:02:00.'])]
    self.interface.dvd = dvd.Dvd('test', [self.title1])
    self.interface.GetDvdInformation(self.input)
    self.mox.ReplayAll()
    test_result = self.interface.EncodeAll(self.input, self.output,
                                           datetime.datetime(1, 1, 1, 0, 2, 0))
    self.assertEqual(test_result, results)
    self.mox.VerifyAll()

  def testEncodeLongTitle(self):
    """Verifies EncodeAll with a title over the time_limit."""
    output = '%stest [Title 2].mp4' % self.output
    self.interface.dvd = dvd.Dvd('test', [self.title2])
    self.interface.GetDvdInformation(self.input)
    handbrake.abs_path.AbsPath(self.output).AndReturn(self.output)
    self.interface.Encode(
        self.input, output, self.title2.number).AndReturn(True)
    self.mox.ReplayAll()
    test_result = self.interface.EncodeAll(self.input, self.output,
                                           datetime.datetime(1, 1, 1, 0, 2, 0))
    self.assertEqual(test_result[0], True)
    self.mox.VerifyAll()

  def testEncodAllMultiple(self):
    """Verifies an entire queue is processed correctly."""
    output1 = '%stest [Title 1].mp4' % self.output
    output2 = '%stest [Title 2].mp4' % self.output
    self.interface.dvd = dvd.Dvd('test', [self.title1, self.title2])
    self.interface.GetDvdInformation(self.input)
    handbrake.abs_path.AbsPath(self.output).AndReturn(self.output)
    self.interface.Encode(
        self.input, output1, self.title1.number).AndReturn(True)
    handbrake.abs_path.AbsPath(self.output).AndReturn(self.output)
    self.interface.Encode(
        self.input, output2, self.title2.number).AndReturn(True)
    self.mox.ReplayAll()
    test_result = self.interface.EncodeAll(self.input, self.output)
    self.assertEqual(test_result, [True, True])
    self.mox.VerifyAll()

if __name__ == '__main__':
  unittest.main()
