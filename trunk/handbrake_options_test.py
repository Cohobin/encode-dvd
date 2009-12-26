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
"""Test suite for handbrake_options."""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'

import unittest
import handbrake_options


class TestHandbrakeOptions(unittest.TestCase):
  """Verifies handbrake_options are correct."""

  def testCorrectIntialization(self):
    """Verifies the options can be built correctly."""
    handbrake_options.Options()

  def testDefaultValues(self):
    """Verifies the default handbreak options are specified correctly."""
    h = handbrake_options.Options()
    for option in h.all:
      self.assertEqual(option.Command(), [])

  def testCustomValues(self):
    """Verifies specified options are processed correctly."""
    x264_options = (
        'ref=1:me=umh:me-range=32:subme=7:analyse=all:filter=0,0:'
        'no-fast-pskip=1:cabac=1:bframes=16:direct=auto:weightb=1:subq=7:'
        'level=4.1')
    h = handbrake_options.Options()
    h.file_format.SetValue('mp4')
    h.file_markers.SetValue(True)
    h.video_encoder.SetValue('x264')
    h.video_x264_opts.SetValue(x264_options)
    h.video_two_pass.SetValue(True)
    h.video_x264_turbo_first_pass.SetValue(True)
    h.video_bitrate.SetValue(1800)
    h.audio_encoder.SetValue('faac')
    h.audio_bitrate.SetValue('384')
    h.audio_mixdown.SetValue('6ch')
    h.audio_dynamic_range_compression.SetValue('1.0')
    h.strict_anamorphic.SetValue(True)
    h.filter_decomb.SetValue('slower')
    h.subtitles_scan.SetValue(True)
    h.subtitles_if_forced.SetValue(True)
    h.subtitles_native_language.SetValue('eng')
    h.file_input.SetValue('/my/movie/dir/')
    h.file_output.SetValue('/my/movie2.mp4')
    h.file_longest_title.SetValue(True)
    self.assertEqual(h.max_size, 100000)
    self.assertEqual(h.general_update.Command(), [])
    self.assertEqual(h.general_verbose.Command(), [])
    self.assertEqual(h.general_cpu.Command(), [])
    self.assertEqual(h.general_preset.Command(), [])
    self.assertEqual(h.file_input.Command(), ['--input', '/my/movie/dir/'])
    self.assertEqual(h.file_title.Command(), [])
    self.assertEqual(h.file_longest_title.Command(), ['--longest'])
    self.assertEqual(h.file_chapters.Command(), [])
    self.assertEqual(h.file_output.Command(), ['--output', '/my/movie2.mp4'])
    self.assertEqual(h.file_format.Command(), ['--format', 'mp4'])
    self.assertEqual(h.file_markers.Command(), ['--markers'])
    self.assertEqual(h.file_large_file_support.Command(), [])
    self.assertEqual(h.file_mp4_web_optimize.Command(), [])
    self.assertEqual(h.file_mp4_ipod_atom.Command(), [])
    self.assertEqual(h.video_encoder.Command(), ['--encoder', 'x264'])
    self.assertEqual(h.video_x264_opts.Command(), ['--x264opts', x264_options])
    self.assertEqual(h.video_two_pass.Command(), ['--two-pass'])
    self.assertEqual(h.video_x264_turbo_first_pass.Command(), ['--turbo'])
    self.assertEqual(h.video_frame_rate.Command(), [])
    self.assertEqual(h.video_quality.Command(), [])
    self.assertEqual(h.video_x264_constant_quantizer.Command(), [])
    self.assertEqual(h.video_target_size.Command(), [])
    self.assertEqual(h.video_bitrate.Command(), ['--vb', '1800'])
    self.assertEqual(h.audio.Command(), [])
    self.assertEqual(h.audio_encoder.Command(), ['--aencoder', 'faac'])
    self.assertEqual(h.audio_bitrate.Command(), ['--ab', '384'])
    self.assertEqual(h.audio_mixdown.Command(), ['--mixdown', '6ch'])
    self.assertEqual(h.audio_sample_rate.Command(), [])
    self.assertEqual(h.audio_dynamic_range_compression.Command(),
                     ['--drc', '1.0'])
    self.assertEqual(h.audio_mp4_track_name.Command(), [])
    self.assertEqual(h.width.Command(), [])
    self.assertEqual(h.height.Command(), [])
    self.assertEqual(h.crop.Command(), [])
    self.assertEqual(h.max_height.Command(), [])
    self.assertEqual(h.max_width.Command(), [])
    self.assertEqual(h.strict_anamorphic.Command(), ['--pixelratio'])
    self.assertEqual(h.loose_anamorphic.Command(), [])
    self.assertEqual(h.color_matrix.Command(), [])
    self.assertEqual(h.filter_deinterlace.Command(), [])
    self.assertEqual(h.filter_decomb.Command(), ['--decomb', 'slower'])
    self.assertEqual(h.filter_detelecine.Command(), [])
    self.assertEqual(h.filter_denoise.Command(), [])
    self.assertEqual(h.filter_deblock.Command(), [])
    self.assertEqual(h.filter_grayscale.Command(), [])
    self.assertEqual(h.subtitles.Command(), [])
    self.assertEqual(h.subtitles_scan.Command(), ['--subtitle-scan'])
    self.assertEqual(h.subtitles_if_forced.Command(), ['--subtitle-forced'])
    self.assertEqual(h.subtitles_native_language.Command(),
                     ['--native-language', 'eng'])


if __name__ == '__main__':
  unittest.main()
