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

import datetime
import unittest
import dvd
from testdata import handbrake_log


class TestBaseDvdObject(unittest.TestCase):
  """Verifies the BaseDvdObject works properly."""

  def setUp(self):
    self.dvd = dvd.BaseDvdObject()

  def testCompare(self):
    """Verifies object comparison work properly."""
    self.dvd.number = 0
    dvd_big = dvd.BaseDvdObject()
    dvd_big.number = 1
    self.assertTrue(self.dvd < dvd_big)
    self.assertTrue(self.dvd == self.dvd)
    self.assertTrue(dvd_big > self.dvd)

  def testCreateDuration(self):
    """Verifies CreateDuration method works properly."""
    date = datetime.datetime(1, 1, 1, 0, 0, 0)
    self.assertEqual(date, self.dvd.CreateDuration('00:00:00'))
    self.assertEqual(date, self.dvd.CreateDuration(date))
    self.assertRaises(dvd.InvalidDuration, self.dvd.CreateDuration, '00 00 00')
    self.assertRaises(dvd.InvalidDuration, self.dvd.CreateDuration, object())

  def testGetDuration(self):
    """Verifies GetDuration method works properly."""
    self.assertEqual('00:00:00', self.dvd.GetDuration())
    self.dvd.duration = datetime.datetime(1, 1, 1, 1, 0, 0)
    self.assertEqual('01:00:00', self.dvd.GetDuration())


class TestChapter(unittest.TestCase):
  """Verifies Chapter class works correctly."""

  def setUp(self):
    self.chapter = dvd.Chapter()
    self.log = handbrake_log.ChapterLineTestData

  def testInvalidIntArguements(self):
    """Verifies invalid Int arguements fail correctly."""
    self.assertRaises(TypeError, dvd.Chapter, start=None)
    self.assertRaises(TypeError, dvd.Chapter, end=None)
    self.assertRaises(TypeError, dvd.Chapter, blocks=None)
    self.assertRaises(TypeError, dvd.Chapter, number=None)
    self.assertRaises(ValueError, dvd.Chapter, start=-1)
    self.assertRaises(ValueError, dvd.Chapter, end=-1)
    self.assertRaises(ValueError, dvd.Chapter, number=-1)

  def testStrictArguements(self):
    """Verifies strict arguement enforcement fails properly."""
    self.assertRaises(ValueError, dvd.Chapter, start=2, end=1, strict=True)
    self.assertRaises(ValueError, dvd.Chapter, blocks=-1, strict=True)

  def testString(self):
    """Verifies the Chapter String method works properly."""
    chapter_str = 'number: 1, start: 0, end: 0, blocks: 0, duration: 00:00:00'
    self.assertEqual(chapter_str, str(self.chapter))

  def testRepr(self):
    """Verifies the Chapter String representation works properly."""
    chapter_repr = ('dvd.Chapter(start=0, end=0, blocks=0, '
                    "duration='00:00:00', number=1, strict=False)")
    self.assertEqual(chapter_repr, repr(self.chapter))

  def testProcessLine(self):
    """Verifies _ProcessLine works correctly."""
    results = self.chapter._ProcessLine(self.log.LINE)
    self.assertEqual(self.log.START, results[0])
    self.assertEqual(self.log.END, results[1])
    self.assertEqual(self.log.BLOCKS, results[2])
    self.assertEqual(self.log.DURATION, results[3])
    self.assertEqual(self.log.NUMBER, results[4])

  def testParseHandbrakeLine(self):
    """Verifies ParseHandbrakeLine works correctly."""
    chapter = dvd.Chapter()
    chapter.ParseHandbrakeLine(self.log.LINE)
    self.assertEqual(self.log.START, chapter.start)
    self.assertEqual(self.log.END, chapter.end)
    self.assertEqual(self.log.BLOCKS, chapter.blocks)
    self.assertEqual(self.log.DURATION, chapter.GetDuration())
    self.assertEqual(self.log.NUMBER, chapter.number)
    self.assertRaises(dvd.InvalidHandbrakeLogLine,
                      self.chapter.ParseHandbrakeLine,
                      self.log.BAD_LINE)


class TestAudio(unittest.TestCase):
  """Verifies Audio class works correctly."""

  def setUp(self):
    self.audio = dvd.Audio()
    self.log = handbrake_log.AudioLineTestData()

  def testInvalidStringArguements(self):
    """Verifies invalid String arguements fail correctly."""
    self.assertRaises(TypeError, dvd.Audio, encoder=1)
    self.assertRaises(TypeError, dvd.Audio, format=1)
    self.assertRaises(TypeError, dvd.Audio, language=1)

  def testInvalidIntArguements(self):
    """Verifies invalid Int arguements fail correctly."""
    self.assertRaises(TypeError, dvd.Audio, sample_rate=None)
    self.assertRaises(TypeError, dvd.Audio, bit_rate=None)
    self.assertRaises(TypeError, dvd.Audio, number=None)

  def testStrictArguements(self):
    """Verifies strict arguement enforcement fails properly."""
    self.assertRaises(ValueError, dvd.Audio, number=-1, strict=True)
    self.assertRaises(ValueError, dvd.Audio, sample_rate=-1, strict=True)
    self.assertRaises(ValueError, dvd.Audio, bit_rate=-1, strict=True)

  def testString(self):
    """Verifies the Audio String method works properly."""
    audio_str = ('number: 1, encoder: AC3, format: 2.0 ch, sample rate: 48000, '
                 'bit rate: 192000, language: English')
    self.assertEqual(audio_str, str(self.audio))

  def testRepr(self):
    """Verifies the Audio String representation works properly."""
    audio_repr = ("dvd.Audio(encoder='AC3', format='2.0 ch', sample_rate=48000,"
                  " bit_rate=192000, language='English', number=1, "
                  'strict=False)')
    self.assertEqual(audio_repr, repr(self.audio))

  def testProcessLine(self):
    """Verifies _ProcessLine works correctly."""
    results = self.audio._ProcessLine(self.log.LINE)
    self.assertEqual(self.log.ENCODER, results[0])
    self.assertEqual(self.log.FORMAT, results[1])
    self.assertEqual(self.log.SAMPLE_RATE, results[2])
    self.assertEqual(self.log.BIT_RATE, results[3])
    self.assertEqual(self.log.LANGUAGE, results[4])
    self.assertEqual(self.log.NUMBER, results[5])

    results = self.audio._ProcessLine(self.log.LINE_TWO)
    self.assertEqual(self.log.ENCODER, results[0])
    self.assertEqual(self.log.FORMAT_TWO, results[1])
    self.assertEqual(self.log.SAMPLE_RATE, results[2])
    self.assertEqual(self.log.BIT_RATE, results[3])
    self.assertEqual(self.log.LANGUAGE, results[4])
    self.assertEqual(self.log.NUMBER, results[5])

  def testParseHandbrakeLine(self):
    """Verifies ParseHandbrakeLine works correctly."""
    self.audio.ParseHandbrakeLine(self.log.LINE)
    self.assertEqual(self.log.ENCODER, self.audio.encoder)
    self.assertEqual(self.log.FORMAT, self.audio.format)
    self.assertEqual(self.log.SAMPLE_RATE, self.audio.sample_rate)
    self.assertEqual(self.log.BIT_RATE, self.audio.bit_rate)
    self.assertEqual(self.log.LANGUAGE, self.audio.language)
    self.assertEqual(self.log.NUMBER, self.audio.number)
    self.assertRaises(dvd.InvalidHandbrakeLogLine,
                      self.audio.ParseHandbrakeLine,
                      self.log.BAD_LINE)


class TestSubtitle(unittest.TestCase):
  """Verifies Subtitle class works correctly."""

  def setUp(self):
    self.subtitle = dvd.Subtitle()
    self.log = handbrake_log.SubtitleLineTestData()

  def testInvalidStringArguements(self):
    """Verifies invalid String arguements fail correctly."""
    self.assertRaises(TypeError, dvd.Subtitle, language=1)
    self.assertRaises(TypeError, dvd.Subtitle, iso_code=1)
    self.assertRaises(TypeError, dvd.Subtitle, iso_language=1)

  def testInvalidIntArguements(self):
    """Verifies invalid Int arguements fail correctly."""
    self.assertRaises(TypeError, dvd.Subtitle, number=None)

  def testStrictArguements(self):
    """Verifies strict arguement enforcement fails properly."""
    self.assertRaises(ValueError, dvd.Subtitle, number=-1, strict=True)

  def testString(self):
    """Verifies the Subtitle String method works properly."""
    subtitle_str = ('number: 1, iso_code: iso639-2, '
                    'iso_language: eng, language: English')
    self.assertEqual(subtitle_str, str(self.subtitle))

  def testRepr(self):
    """Verifies the Subtitle String representation works properly."""
    subtitle_repr = ("dvd.Subtitle(language='English', iso_code='iso639-2', "
                     "iso_language='eng',  number=1, strict=False)")
    self.assertEqual(subtitle_repr, repr(self.subtitle))

  def testProcessLine(self):
    """Verifies _ProcessLine works correctly."""
    results = self.subtitle._ProcessLine(self.log.LINE)
    self.assertEqual(self.log.LANGUAGE, results[0])
    self.assertEqual(self.log.ISO_CODE, results[1])
    self.assertEqual(self.log.ISO_LANGUAGE, results[2])
    self.assertEqual(self.log.NUMBER, results[3])

    results = self.subtitle._ProcessLine(self.log.LINE_TWO)
    self.assertEqual(self.log.LANGUAGE, results[0])
    self.assertEqual(self.log.ISO_CODE, results[1])
    self.assertEqual(self.log.ISO_LANGUAGE, results[2])
    self.assertEqual(self.log.NUMBER, results[3])

  def testParseHandbrakeLine(self):
    """Verifies ParseHandbrakeLine works correctly."""
    self.subtitle.ParseHandbrakeLine(self.log.LINE)
    self.assertEqual(self.log.LANGUAGE, self.subtitle.language)
    self.assertEqual(self.log.ISO_CODE, self.subtitle.iso_code)
    self.assertEqual(self.log.ISO_LANGUAGE, self.subtitle.iso_language)
    self.assertEqual(self.log.NUMBER, self.subtitle.number)
    self.assertRaises(dvd.InvalidHandbrakeLogLine,
                      self.subtitle.ParseHandbrakeLine,
                      self.log.BAD_LINE)


class TestTitle(unittest.TestCase):
  """Verifies Title class works correctly."""

  def setUp(self):
    self.title = dvd.Title()
    self.strict_title = dvd.Title(strict=True)

  def testInvalidIntArguements(self):
    """Verifies invalid Int arguements fail correctly."""
    self.assertRaises(TypeError, dvd.Title, video_tile_set=None)
    self.assertRaises(TypeError, dvd.Title, number=None)
    self.assertRaises(TypeError, dvd.Title, cell_end=None)
    self.assertRaises(TypeError, dvd.Title, cell_blocks=None)
    self.assertRaises(TypeError, dvd.Title, horizontal_size=None)
    self.assertRaises(TypeError, dvd.Title, vertical_size=None)
    self.assertRaises(TypeError, dvd.Title, autocrop_top=None)
    self.assertRaises(TypeError, dvd.Title, autocrop_bottom=None)
    self.assertRaises(TypeError, dvd.Title, autocrop_left=None)
    self.assertRaises(TypeError, dvd.Title, autocrop_right=None)
    self.assertRaises(ValueError, dvd.Title, video_tile_set=-1)
    self.assertRaises(ValueError, dvd.Title, horizontal_size=-1)
    self.assertRaises(ValueError, dvd.Title, vertical_size=-1)
    self.assertRaises(ValueError, dvd.Title, autocrop_top=-1)
    self.assertRaises(ValueError, dvd.Title, autocrop_bottom=-1)
    self.assertRaises(ValueError, dvd.Title, autocrop_left=-1)
    self.assertRaises(ValueError, dvd.Title, autocrop_right=-1)

  def testInvalidFloatArguements(self):
    """Verifies invalid Float arguements fail correctly."""
    self.assertRaises(TypeError, dvd.Title, aspect_ratio=None)
    self.assertRaises(TypeError, dvd.Title, frame_rate=None)

  def testDuration(self):
    """Verifies Duration arguements are handled properly."""
    title_datetime = dvd.Title(duration=datetime.datetime(1, 1, 1, 0, 0, 0))
    self.assertEqual(datetime.datetime(1, 1, 1, 0, 0, 0), self.title.duration)
    self.assertEqual(datetime.datetime(1, 1, 1, 0, 0, 0),
                     title_datetime.duration)
    self.assertRaises(TypeError, dvd.Title, duration='00 00:00:00')
    self.assertRaises(TypeError, dvd.Title, duration=None)

  def testStrictArguements(self):
    """Verifies strict arguement enforcement fails properly."""
    self.assertRaises(ValueError, dvd.Title, cell_start=2,
                      cell_end=1, strict=True)
    self.assertRaises(ValueError, dvd.Title, cell_start=-1, strict=True)
    self.assertRaises(ValueError, dvd.Title, cell_end=-1, strict=True)
    self.assertRaises(ValueError, dvd.Title, cell_blocks=-1, strict=True)
    self.assertRaises(ValueError, dvd.Title, number=-1, strict=True)

  def testGetDuration(self):
    """Verifies GetDuration works properly."""
    title = dvd.Title(duration='01:10:20')
    self.assertEqual('01:10:20', title.GetDuration())

  def testAddChapterByObject(self):
    """Verifies adding a single Chapter object to a Title object works."""
    chapter = dvd.Chapter(number=3)

    self.assertFalse(self.title.AddChapter())
    self.assertEqual(len(self.title.chapters), 0)

    self.assertFalse(self.title.AddChapter(1))
    self.assertEqual(len(self.title.chapters), 0)

    self.assertTrue(self.title.AddChapter(chapter))
    self.assertEqual(len(self.title.chapters), 1)
    self.assertEqual(self.title.chapters[0].number, 3)

  def testAddChapterByArgs(self):
    """Verifies adding a Chapter to a Tilte by Chapter arguments works."""
    args = [0, 0, 0, '00:00:00', 4]
    invalid_args = [None, None, None, None, None]

    self.assertFalse(self.title.AddChapter(*invalid_args))
    self.assertEqual(len(self.title.chapters), 0)

    self.assertTrue(self.title.AddChapter(*args))
    self.assertEqual(len(self.title.chapters), 1)
    self.assertEqual(self.title.chapters[0].number, 4)

    self.assertTrue(self.strict_title.AddChapter(*args))
    self.assertEqual(len(self.strict_title.chapters), 1)
    self.assertEqual(self.strict_title.chapters[0].number, 4)
    self.assertTrue(self.strict_title.chapters[0].strict)

  def testAddChapterMultipleObjects(self):
    """Verifies adding multiple Chapter objects at once works properly."""
    chapters = [dvd.Chapter(), dvd.Chapter(number=2)]

    self.assertFalse(self.title.AddChapter(1, 2))
    self.assertEqual(len(self.title.chapters), 0)

    self.assertTrue(self.title.AddChapter(*chapters))
    self.assertEqual(len(self.title.chapters), 2)
    self.assertEqual(self.title.chapters[1].number, 2)

  def testAddAudioByObject(self):
    """Verifies adding a single Audio object to a Title object works."""
    audio = dvd.Audio(number=3)

    self.assertFalse(self.title.AddAudio())
    self.assertEqual(len(self.title.audio), 0)

    self.assertFalse(self.title.AddAudio(1))
    self.assertEqual(len(self.title.audio), 0)

    self.assertTrue(self.title.AddAudio(audio))
    self.assertEqual(len(self.title.audio), 1)
    self.assertEqual(self.title.audio[0].number, 3)

  def testAddAudioByArgs(self):
    """Verifies adding a Audio to a Tilte by Audio arguments works."""
    args = ['AC3', '2.0 ch', 48000, 192000, 'English', 4]
    invalid_args = [None, None, None, None, None, None]

    self.assertFalse(self.title.AddAudio(*invalid_args))
    self.assertEqual(len(self.title.audio), 0)

    self.assertTrue(self.title.AddAudio(*args))
    self.assertEqual(len(self.title.audio), 1)
    self.assertEqual(self.title.audio[0].number, 4)

    self.assertTrue(self.strict_title.AddAudio(*args))
    self.assertEqual(len(self.strict_title.audio), 1)
    self.assertEqual(self.strict_title.audio[0].number, 4)
    self.assertTrue(self.strict_title.audio[0].strict)

  def testAddAudioMultipleObjects(self):
    """Verifies adding multiple Audio objects at once works properly."""
    audio = [dvd.Audio(), dvd.Audio(number=2)]

    self.assertFalse(self.title.AddAudio(1, 2))
    self.assertEqual(len(self.title.audio), 0)

    self.assertTrue(self.title.AddAudio(*audio))
    self.assertEqual(len(self.title.audio), 2)
    self.assertEqual(self.title.audio[1].number, 2)

  def testAddSubtitleByObject(self):
    """Verifies adding a single Subtitle object to a Title object works."""
    subtitle = dvd.Subtitle(number=3)

    self.assertFalse(self.title.AddSubtitle())
    self.assertEqual(len(self.title.subtitles), 0)

    self.assertFalse(self.title.AddSubtitle(1))
    self.assertEqual(len(self.title.subtitles), 0)

    self.assertTrue(self.title.AddSubtitle(subtitle))
    self.assertEqual(len(self.title.subtitles), 1)
    self.assertEqual(self.title.subtitles[0].number, 3)

  def testAddSubtitleByArgs(self):
    """Verifies adding a Subtitle to a Tilte by Subtitle arguments works."""
    args = ['English', 'iso639-2', 'eng', 4]
    invalid_args = [None, None, None, None]

    self.assertFalse(self.title.AddSubtitle(*invalid_args))
    self.assertEqual(len(self.title.subtitles), 0)

    self.assertTrue(self.title.AddSubtitle(*args))
    self.assertEqual(len(self.title.subtitles), 1)
    self.assertEqual(self.title.subtitles[0].number, 4)

    self.assertTrue(self.strict_title.AddSubtitle(*args))
    self.assertEqual(len(self.strict_title.subtitles), 1)
    self.assertEqual(self.strict_title.subtitles[0].number, 4)
    self.assertTrue(self.strict_title.subtitles[0].strict)

  def testAddSubtitleMultipleObjects(self):
    """Verifies adding multiple Subtitle objects at once works properly."""
    subtitles = [dvd.Subtitle(), dvd.Subtitle(number=2)]

    self.assertFalse(self.title.AddSubtitle(1, 2))
    self.assertEqual(len(self.title.subtitles), 0)

    self.assertTrue(self.title.AddSubtitle(*subtitles))
    self.assertEqual(len(self.title.subtitles), 2)
    self.assertEqual(self.title.subtitles[1].number, 2)

  def testCompare(self):
    """Verifies two audio objects can be compared correctly."""
    title_one = dvd.Title(number=1)
    title_two = dvd.Title(number=2)
    self.assertTrue(title_one < title_two)

  def testString(self):
    """Verifies the Title String method works properly."""
    title_str = (
        'video_tile_set: 1, number: 1, cell_start: 0, cell_end: 0, '
        'cell_blocks: 0, duration: 00:00:00, horizontal_size: 720, '
        'vertical_size: 480, aspect_ratio: 1.33, frame_rate: 29.97, '
        'autocrop_top: 0, autocrop_bottom: 0, autocrop_left: 0, '
        'autocrop_right: 0, combining: False, chapters: [], audio: [], '
        'subtitles: []')
    self.assertEqual(title_str, str(self.title))

  def testRepr(self):
    """Verifies the Title String representation works properly."""
    title_repr = (
        'dvd.Title(video_tile_set=1, number=1, cell_start=0, cell_end=0, '
        "cell_blocks=0, duration='00:00:00', horizontal_size=720, "
        'vertical_size=480, aspect_ratio=1.33, frame_rate=29.97, '
        'autocrop_top=0, autocrop_bottom=0, autocrop_left=0, autocrop_right=0, '
        'combining=False, chapters=[], audio=[], subtitles=[], strict=False)')
    self.assertEqual(title_repr, repr(self.title))


class TestDvd(unittest.TestCase):
  """Verifies Dvd class works correctly."""

  def setUp(self):
    self.dvd = dvd.Dvd()
    self.strict_dvd = dvd.Dvd(strict=True)

  def testDvdInit(self):
    """Verifies Dvd initalization works properly."""
    datetime.datetime.strptime(self.dvd.name, '%Y-%m-%d_%H-%M-%S')
    dvd_name = dvd.Dvd('Name')
    self.assertEqual(dvd_name.name, 'Name')

  def testAddTitle(self):
    """Verifies AddTitle works properly."""
    self.assertFalse(self.dvd.AddTitle())
    self.assertEqual(len(self.dvd.titles), 0)

    self.assertFalse(self.dvd.AddTitle(1))
    self.assertEqual(len(self.dvd.titles), 0)

    self.assertTrue(self.dvd.AddTitle(dvd.Title()))
    self.assertEqual(len(self.dvd.titles), 1)
    self.assertEqual(self.dvd.titles[0].number, 1)

  def testGetTitle(self):
    """Verifies GetTitle works properly."""
    self.assertRaises(dvd.TitleNotFoundError, self.dvd.GetTitle, 1)
    self.assertTrue(self.dvd.AddTitle(dvd.Title()))
    self.assertRaises(dvd.TitleNotFoundError, self.dvd.GetTitle, 2)
    title = self.dvd.GetTitle(1)
    self.assertEqual(title.number, 1)

  def testProcessTitleSection(self):
    """Verifies _ProcessTitleSection works correctly."""
    log = handbrake_log.TitleSectionTestData()

    self.assertEqual(
        self.dvd._ProcessTitleSection(log.CHAPTER_LOG, dvd.Chapter),
        [dvd.Chapter(*log.CHAPTER_ARGS)])

    self.assertEqual(
        self.dvd._ProcessTitleSection(log.AUDIO_LOG, dvd.Audio),
        [dvd.Audio(*log.AUDIO_ARGS)])

    self.assertEqual(
        self.dvd._ProcessTitleSection(log.SUBTITLE_LOG, dvd.Subtitle),
        [dvd.Subtitle(*log.SUBTITLE_ARGS)])

    self.assertEqual(
        self.dvd._ProcessTitleSection(['+  '], dvd.Chapter),
        [])

  def testParseVideoTileSetLine(self):
    """Verifies _ParseVideoTileSetLine works correctly."""
    log = handbrake_log.ParseVideoTileSetLineTestData()
    results = self.dvd._ParseVideoTileSetLine(log.LINE)
    self.assertEqual(log.TILE, results[0])
    self.assertEqual(log.START, results[1])
    self.assertEqual(log.END, results[2])
    self.assertEqual(log.BLOCKS, results[3])

  def testParseDurationLine(self):
    """Verifies _ParseDurationLine works correctly."""
    log = handbrake_log.ParseDurationLineTestData()
    self.assertEqual(log.DURATION, self.dvd._ParseDurationLine(log.LINE))

  def testParseSizeLine(self):
    """Verifies _ParseSizeLine works correctly."""
    log = handbrake_log.ParseSizeLineTestData()
    results = self.dvd._ParseSizeLine(log.LINE)
    self.assertEqual(log.HORIZONTAL_SIZE, results[0])
    self.assertEqual(log.VERTICAL_SIZE, results[1])
    self.assertEqual(log.ASPECT, results[2])
    self.assertEqual(log.FRAME_RATE, results[3])

  def testParseAutoCropLine(self):
    """Verifies _ParseAutoCropLine works correctly."""
    log = handbrake_log.ParseAutocropLineTestData()
    results = self.dvd._ParseAutoCropLine(log.LINE)
    self.assertEqual(log.TOP, results[0])
    self.assertEqual(log.BOTTOM, results[1])
    self.assertEqual(log.LEFT, results[2])
    self.assertEqual(log.RIGHT, results[3])

  def testExtractTitleFromLog(self):
    """Verifies _ExtractLog works correctly."""
    log = handbrake_log.ExtractTitleFromLogTestData()

    title, chapter, audio, subtitle = self.dvd._ExtractTitleFromLog(log.log)
    self.assertEqual(log.INDEXES, [chapter, audio, subtitle])
    self.assertEqual(dvd.Title(*log.TITLE_ARGS), title)

  def testProcessTitle(self):
    """Verifies ProcessHandbrakeAnalysis works correctly."""
    log = handbrake_log.ExtractTitleFromLogTestData()
    self.dvd._ProcessTitle(log.log)
    self.assertEqual(len(self.dvd.titles[0].chapters), 21)
    self.assertEqual(len(self.dvd.titles[0].audio), 4)
    self.assertEqual(len(self.dvd.titles[0].subtitles), 4)

  def testIndexHandbrakeLog(self):
    """Verifies _IndexHandbrakeLog works correctly."""
    log = handbrake_log.IndexHandbrakeLogTestData()
    titles, dvd_name = self.dvd._IndexHandbrakeLog(log.log)
    self.assertEqual(titles, log.TITLES)
    self.assertEqual(dvd_name, log.NAME)

  def testProcessHandbrakeAnalysis(self):
    """Verifies ProcessHandbrakeAnalysis works correctly."""
    log = handbrake_log.IndexHandbrakeLogTestData()
    self.dvd.ProcessHandbrakeAnalysis(log.log_raw)
    self.assertEqual(self.dvd.name, log.NAME)
    for x in xrange(len(self.dvd.titles)):
      self.assertEqual(len(self.dvd.titles[x].chapters),
                       log.DVD_SIGNATURE[x][0])
      self.assertEqual(len(self.dvd.titles[x].audio),
                       log.DVD_SIGNATURE[x][1])
      self.assertEqual(len(self.dvd.titles[x].subtitles),
                       log.DVD_SIGNATURE[x][2])

  def testDetermineDvdName(self):
    """Verifies _DetermineDvdName works correctly."""
    self.assertEqual(self.dvd._DetermineDvdName('Opening /tmp/ghosts/...'),
                     'ghosts')
    self.assertEqual(self.dvd._DetermineDvdName('Opening /tmp/ghosts...'),
                     'ghosts')
    self.assertEqual(self.dvd._DetermineDvdName('/tmp/ghosts'), None)
    self.assertEqual(self.dvd._DetermineDvdName('Opening FIREFLY_D1...'),
                     'FIREFLY_D1')

  def testString(self):
    """Verifies the Dvd String method works properly."""
    dvd_str = 'name: Test, titles: []'
    self.assertEqual(dvd_str, str(dvd.Dvd('Test')))

  def testRepr(self):
    """Verifies the Dvd String representation works properly."""
    dvd_repr = "dvd.Dvd(name='Test', titles=[], strict=False)"
    self.assertEqual(dvd_repr, repr(dvd.Dvd('Test')))


class TestIntegration(unittest.TestCase):
  """Verifies multiple DVD's are processed correctly without crashing."""

  def testMultipleDvdReads(self):
    """Verifies that multiple DVD's can be read correctly."""
    data = handbrake_log.IntegrationTest()
    for source_file in data.files:
      dvd_disc = dvd.Dvd()
      file_handle = open(source_file)
      log = file_handle.readlines()
      file_handle.close()
      dvd_disc.ProcessHandbrakeAnalysis(log)


if __name__ == '__main__':
  unittest.main()
