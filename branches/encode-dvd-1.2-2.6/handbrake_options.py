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
"""Python HandBrake options."""

__author__ = 'Robert M. Pufky (robert.pufky@gmail.com)'
__version__ = '1.0'

import options


class Options(object):
  """Enumerates current handbrake options in 0.9.3.

  This enumerates all of the options that are set across all encodes.  It is
  also to help so you don't have to keep going back and forth between the
  command line and this module.

  Useful sites on HandBrakeCLI: http://trac.handbrake.fr/wiki/CLIGuide
  Useful sites on x264:         http://mewiki.project357.com/wiki/X264_Settings
                                http://trac.handbrake.fr/wiki/x264Options

  Decriptions of the option types (Set, Range, Integer, Float, String) can be
  found in the options class.

  Attributes:
    max_size: Integer reasonable max integer option size.
    general_update: BooleanOption Tell HandBrake to check for updates, print
      version information and exit.
    general_verbose: RangeOption Verbosity to use.  From 0-3, default 0.
    general_cpu: RangeOption Number of CPU's to use.  From 1-X, default
      autodetect.
    general_preset: StringOption Use built-in present (try HandBrakeCLI
      --preset-list), instead of defining encoding settings on the command line.
      Case sensitive.  http://trac.handbrake.fr/wiki/CLIGuide#presets.  Default
      do not use preset.
    file_input: StringOption Set input device.  Can be path to file or
      directory.  Directories require trailing slash.  REQUIRED.
    file_title: RangeOption Select title to use on DVD. From 0-X, 0 scans
      titles, default 1.
    file_longest_title: BooleanOption Select the longest title to encode on DVD
      automatically.
    file_chapters: StringOption Select video chapters to encode.  From 1-X,
      default all chapters.
    file_output: StringOption Set output file, with path to file.  REQUIRED.
    file_format: SetOption Set output file format (avi,mp4,ogm,mkv), default
      autodetect based on output filename extension.
    file_markers: BooleanOption Add chapter markers for mp4, mkv files if they
      are avaliable.  If not mp4, mkv, this does nothing.  Default no chapter
      markers.
    file_large_file_support: BooleanOption Use 64-bit mp4 files for > 4GB output
      file support.  This breaks PS3, iPod playback.  Default no support (up to
      4GB files).
    file_mp4_web_optimize: BooleanOption Optimize mp4 files for streaming over
      the web.  If not mp4, this does nothing.  Default no optimization.
    file_mp4_ipod_atom: BooleanOption Mark mp4 files so 5.5G iPods will play
      them.  If not mp4, this does nothing.  Default no atoms.
    video_encoder: SetOption Set video encoder to encode with
      (ffmpeg,xvid,x264,theora).  Default ffmpeg.
    video_x264_opts: StringOption Use advanced x264 options, using the mencoder
      option format style: option1=value1:option2=value2.  This does nothing if
      not a x264 encoding.  x264 options can be found at:
      http://trac.handbrake.fr/wiki/x264Options.  Default no advanced options.
    video_two_pass: BooleanOption Use two passes to encode video.  Slower, but
      better encode.  Default one pass.
    video_x264_turbo_first_pass: BooleanOption If using VIDEO_TWO_PASS and
      encoding with x264, use this option to increase first pass speed 2-4x,
      affecting PSNR +/-0.05dB.  If not x264, this does nothing.  Default no.
    video_frame_rate: SetOption Set video framerate to a constant
      (5/10/12/15/23.976/24/25/29.97).  Defaults to source framerate if codec
      supports it, otherwise auto-selects a constant frame rate and fills in
      frames for codecs that do not support it (namely, avi).  This should
      usually be left alone.  Information at:
      http://trac.handbrake.fr/wiki/FramerateGuide.  Default autodetect.
    video_quality: RangeOption Use constant video quality, From 0.0-1.0.  Using
      1.0 will usually lead to files larger than the source file.
      VIDEO_BITRATE, VIDEO_TWO_PASS, and VIDEO_TARGET_SIZE cannot be used with
      this options.  Default no constant video quality.
    video_x264_constant_quantizer: SetOption Use with VIDEO_QUALITY to use CQP
      (constant quantizer paramter) instead of CRF (constant rate factor) for
      encode.  This dynamically adjusts compression based on what is happening
      in the frame allowing for a smaller, but higher quality encode.  Does
      nothing if not using x264.  More info at:
      http://forum.handbrake.fr/viewtopic.php?f=5&t=231.  Default CRF (with
      VIDEO_QUALITY).
    video_target_size: IntegerOption Set target size of output file in MB.  Must
      specify FILE_LARGE_FILE_SUPPORT if specifying a file > 4000MB.  Cannot be
      used with VIDEO_QUALITY or VIDEO_BITRATE.  Default no target size.
    video_bitrate: IntegerOption Set video bitrate in kb/s.  Cannot be used with
      VIDEO_TARGET_SIZE or VIDEO_QUALITY.  Default 1000.
    audio: StringOption Set audio tracks to encode from source.  Can specify
      multiple tracks, including the same track multiple times, to be used for
      encoding with other audio options.  Tracks must be comma separated, and
      the same number must be used in other audio options.  Can specify 'none'
      to remove audio from encoded video.  Example options: 1,1,2,3 or none.
      Default track 1.
    audio_encoder: SetOption Set audio encoder (faac/lame/vorbis/ac3), to use.
      Can be separated by commas for multiple audio streams.
      Example: faac,ac3,lame,vorbis.  Defaults are AAC for .mp4, MP3 for .avi,
      Vorbis for .ogm, and AC3 for .mkv.
    audio_bitrate: StringOption Set audio bitrate for codec, separated by commas
      for multiple streams.  AC3 ignores this option, but it must be specified
      if using multiple audio streams.  Example: 128,384,192,auto.
      Default 160 for all streams.
    audio_mixdown: StringOption Surround sound downmixing format
      (mono/stereo/dpl1/dpl2/6ch/auto), separated by commas for multiple
      streams.  AC3 ignores this option, but it must be specified if using
      multiple audio streams.  Example: 6ch,dpl2,dpl1,auto.  Default dpl2
      (Dolby Pro-Logic 2).  http://trac.handbrake.fr/wiki/SurroundSoundGuide.
    audio_sample_rate: StringOption Set audio samplerate  in kilohertz
      (22.05/24/32/44.1/48) plus any other values supported by audio encoder.
      For multiple audio stream, separate by commas.  Example: 24,44.1,44.1,48.
      AC3 ignores this option, but must be specified if using multiple streams.
      Default rate is same as source, or best alternative rate.
    audio_dynamic_range_compression: StringOption Dynamic range compression,
      making soft sounds louder without changing louder sounds.  From 1.0 (off)
      to 4.0 (max loudest for all sounds).  Effective settings are between
      1.5-2.5.  Can be used for multiple streams, but must be comma separated.
      AC3 ignores this option, but must be specified in multiple streams.
      Example: 1.5,1.5,1.5,1.0.  Default 1.0.
    audio_mp4_track_name: StringOption Audio track name, separated by commas for
      multiple tracks.  If not mp4 file, this option is ignored.
      Example: 'Main Track - AAC','Main Track - AC3','Commentary','Extras'.
      Must be used for AppleTV encodes with multiple streams.  Default none.
    width: IntegerOption Set picture width in pixels, 720 widescreen, 640
      fullscreen.  If no HEIGHT is specified, it will calculate a height to
      preserve aspect ratio.  Default autodetect ratio and appropriate width.
    height: IntegerOption Set picture height in pixels.  If no WIDTH is
      specified, it will calculate a width to preserve aspect ratio.  Default
      autodetect ratio and appropriate height.
    crop: StringOption Set cropping values ([Top:Bottom:Left:Right],autocrop) in
      pixels.  Autocrap will automatically detect and remove bars.  Default
      autocrop.
    max_height: IntegerOption Set maximum allowed height in pixels, anything
      over will be scaled with width to fit and preserve aspect ratio.  Default
      no max.
    max_width: IntegerOption Set maximum allowed width in pixels, anythin over
      will be scaled with height to fit and preserve aspect ratio.  Default no
      max.
    strict_anamorphic: BooleanOption Store pixel aspect ratio in video stream
      (strict anamorphic).  Should use this option for best encoded videos.
      http://trac.handbrake.fr/wiki/AnamorphicGuide.  Default no strict.
    loose_anamorphic: StringOption Divides dimensions cleanly by 16, and
      optionally the pixel ratio to use.  Useful for x264 encoding.  Allows
      scaling down by giving WIDTH.  Example 8 or 8:1.33:1.
      http://trac.handbrake.fr/wiki/AnamorphicGuide#loose.
      http://trac.handbrake.fr/wiki/AnamorphicGuide#itu.  Default 16:auto.
    color_matrix: SetOption Set color space for video (601,709).  601 - standard
      definition, 709 - high definition.  Default set by resolution.
    filter_deinterlace: StringOption Deinterlace video with yadif/mcdeint
      filter.  Can specify by speed (fast,slow,slower) or filter specification
      <YM:FD:MM:QP>.  It is almost always better to use FILTER_DECOMB.
      http://trac.handbrake.fr/wiki/DeinterlacingGuide.  Default 0:-1:-1:1
      (fast).
    filter_decomb: StringOption Selectively deinterlace when combing is
      detected.  By default runs as 'slower' option for deinterlace.  Can use
      filter specification <MO:ME:MT:ST:BT:BX:BY>.
      http://trac.handbrake.fr/wiki/Decomb.  Default 1:2:6:9:80:16:16.
    filter_detelecine: StringOption Inverse telecine (ivtc) pullup filter
      (<L:R:T:B:SB:MP>).  Restores video to progressive if framerate different
      than source.  Drops duplicate frames to restore the pre-telecine
      framerate, unless you specify a constant framerate VIDEO_FRAME_RATE.
      Default 1:1:4:4:0:0.
    filter_denoise: StringOption Denoise video with hqdn3d filter
      (<SL:SC:TL:TC>) or by strength (weak,medium,strong).  Default 4:3:6:4.5
      (between medium and strong).
    filter_deblock: StringOption Deblock video with pp7 filter.  From 1-10, or
      <QP:M>.  1 very little deblocking, 10 may be too blurry.  Default 5 (5:2).
    filter_grayscale: BooleanOption Enable Grayscale encoding.  Useful to
      encode black and white videos in true black and white.  Default off.
    subtitles: RangeOption Select subtitle track to use, From 1-X.  This will
      force handbrake to hard-burn the subtitles into the movie, you will NOT be
      able to turn them off.  Default no subtitles.
    subtitles_scan: BooleanOption Scan for subtitles in an extra 1st pass, and
      choose the one that is only used 10 percent of the time or less.  This
      should locate subtitles for short foreign language segments.  Should be
      used with SUBTITLES_FORCED.  Default no scan.
    subtitles_if_forced: BooleanOption Only display subtitles from the selected
      stream if the subtitle has the forced flag set.  May be used in
      conjunction with SUBTITLES_SCAN to auto-select a stream if it contains
      forced subtitles.  Default no forced subtitles.
    subtitles_native_language: StringOption Use subtitles in specified
      languages, if audio differs from your native language.  Can specify any
      ISO639-2 language, example eng.  Full list:
      http://www.loc.gov/standards/iso639-2/php/code_list.php.  Default none.
    all: List containing all handbrake options.
  """

  def __init__(self):
    self.max_size = 100000
    self.general_update = options.BooleanOption(
        long='--update', short='-u', description='Tell HandBrake to check for '
        'updates, print version information and exit.  NO OPTIONS.',
        default=None)
    self.general_verbose = options.RangeOption(
        long='--verbose', short='-v', description='Verbosity to use.  From 0-3,'
        ' default 0.', low=0, high=3, default=0)
    self.general_cpu = options.RangeOption(
        long='--cpu', short='-C', description="Number of CPU's to use.  From "
        '1-X, default autodetect.', low=1, high=self.max_size, default=None)
    self.general_preset = options.StringOption(
        long='--preset', short='-Z', description='Use built-in present (try '
        '--preset-list), instead of defining encoding settings on the command '
        'line.  Case sensitive. http://trac.handbrake.fr/wiki/CLIGuide#presets.'
        '  Default do not use preset.', default=None)
    self.file_input = options.StringOption(
        long='--input', short='-i', description='Set input device.  Can be path'
        ' to file or directory.  Directories require trailing slash.  '
        'REQUIRED.', default=None)
    self.file_title = options.RangeOption(
        long='--title', short='-t', description='Select title to use on DVD. '
        'From 0-X, 0 scans titles, default 1.', low=0, high=self.max_size,
        default=1)
    self.file_longest_title = options.BooleanOption(
        long='--longest', short='-L', description='Select the longest title to '
        'encode on DVD automatically.  NO OPTIONS.', default=None)
    self.file_chapters = options.StringOption(
        long='--chapters', short='-c', description='Select video chapters to '
        'encode.  From 1-X, default all chapters.', default='all')
    self.file_output = options.StringOption(
        long='--output', short='-o', description='Set output file, with path to'
        ' file.  REQUIRED.', default=None)
    self.file_format = options.SetOption(
        long='--format', short='-f', description='Set output file format '
        '(avi,mp4,ogm,mkv), default autodetect based on filename extension.',
        set=['avi', 'mp4', 'ogm', 'mkv'], default=None)
    self.file_markers = options.BooleanOption(
        long='--markers', short='-m', description='Add chapter markers for mp4,'
        ' mkv files if they are avaliable.  If not mp4, mkv, this does nothing.'
        '  Default no chapter markers.  NO OPTIONS.', default=None)
    self.file_large_file_support = options.BooleanOption(
        long='--large-file', short='-4', description='Use 64-bit mp4 files for '
        '> 4GB output file support.  This breaks PS3, iPod playback.  Default '
        'no support (up to 4GB files).  NO OPTIONS.', default=None)
    self.file_mp4_web_optimize = options.BooleanOption(
        long='--optimize', short='-O', description='Optimize mp4 files for '
        'streaming over the web.  If not mp4, this does nothing.  Default no '
        'optimization.  NO OPTIONS.', default=None)
    self.file_mp4_ipod_atom = options.BooleanOption(
        long='--ipod-atom', short='-I', description='Mark mp4 files so 5.5G '
        'iPods will play them.  If not mp4, this does nothing.  Default no '
        'atoms.  NO OPTIONS.', default=None)
    self.video_encoder = options.SetOption(
        long='--encoder', short='-e', description='Set video encoder to encode '
        'with (ffmpeg,xvid,x264,theora).  Default ffmpeg.',
        set=['ffmpeg', 'xvid', 'x264', 'theora'], default='ffmpeg')
    self.video_x264_opts = options.StringOption(
        long='--x264opts', short='-x', description='Use advanced x264 options, '
        'using the mencoder option format style: option1=value1:option2=value2.'
        '  This does nothing if not a x264 encoding.  x264 options can be found'
        ' at: http://trac.handbrake.fr/wiki/x264Options.  Default no advanced '
        'options.', default=None)
    self.video_two_pass = options.BooleanOption(
        long='--two-pass', short='-q', description='Use two passes to encode '
        'video.  Slower, but better encode.  Default one pass.  NO OPTIONS.',
        default=None)
    self.video_x264_turbo_first_pass = options.BooleanOption(
        long='--turbo', short='-T', description='If using VIDEO_TWO_PASS and '
        'encoding with x264, use this option to increase first pass speed 2-4x,'
        ' affecting PSNR +/-0.05dB.  If not x264, this does nothing.  Default '
        'no.  NO OPTIONS.', default=None)
    self.video_frame_rate = options.SetOption(
        long='--rate', short='-r', description='Set video framerate to a '
        'constant (5/10/12/15/23.976/24/25/29.97).  Defaults to source '
        'framerate if codec supports it, otherwise auto-selects a constant '
        'frame rate and fills in frames for codecs that do not support it '
        '(namely, avi).  This should usually be left alone.  Information at: '
        'http://trac.handbrake.fr/wiki/FramerateGuide.  Default autodetect.',
        set=[5, 10, 12, 15, 23.976, 24, 25, 29.97], default=None)
    self.video_quality = options.RangeOption(
        long='--quality', short='-q', description='Use constant video quality, '
        'From 0.0-1.0.  Using 1.0 will usually lead to files larger than the '
        'source file.  VIDEO_BITRATE, VIDEO_TWO_PASS, and VIDEO_TARGET_SIZE '
        'cannot be used with this options.  Default no constant video quality.',
        low=0.0, high=1.0, default=None)
    self.video_x264_constant_quantizer = options.SetOption(
        long='--cqp', short='-Q', description='Use with VIDEO_QUALITY to use '
        'CQP (constant quantizer paramter) instead of CRF (constant rate '
        'factor) for encode.  This dynamically adjusts compression based on '
        'what is happening in the frame allowing for a smaller, but higher '
        'quality encode.  Does nothing if not using x264.  More info at: '
        'http://forum.handbrake.fr/viewtopic.php?f=5&t=231.  '
        'Default CRF (with VIDEO_QUALITY).', set=['CRF', 'CQP'], default=None)
    self.video_target_size = options.IntegerOption(
        long='--size', short='-S', description='Set target size of output file '
        'in MB.  Must specify FILE_LARGE_FILE_SUPPORT if specifying a file > '
        '4000MB.  Cannot be used with VIDEO_QUALITY or VIDEO_BITRATE.  Default '
        'no target size.', default=None)
    self.video_bitrate = options.IntegerOption(
        long='--vb', short='-b', description='Set video bitrate in kb/s.  '
        'Cannot be used with VIDEO_TARGET_SIZE or VIDEO_QUALITY.  Default '
        '1000.', default=1000)
    self.audio = options.StringOption(
        long='--audio', short='-a', description='Set audio tracks to encode '
        'from source.  Can specify multiple tracks, including the same track '
        'multiple times, to be used for encoding with other audio options.  '
        'Tracks must be comma separated, and the same number must be used in '
        "other audio options.  Can specify 'none' to remove audio from encoded "
        'video.  Example options: 1,1,2,3 or none.  Default track 1.',
        default='1')
    self.audio_encoder = options.SetOption(
        long='--aencoder', short='-E', description='Set audio encoder '
        '(faac/lame/vorbis/ac3), to use.  Can be separated by commas for '
        'multiple audio streams.  Example (from AUDIO example) faac,ac3,lame,'
        'vorbis.  Defaults are AAC for .mp4, MP3 for .avi, Vorbis for .ogm, and'
        ' AC3 for .mkv. (autodetect).', set=['faac', 'lame', 'vorbis', 'ac3'],
        default=None)
    self.audio_bitrate = options.StringOption(
        long='--ab', short='-B', description='Set audio bitrate for codec, '
        'separated by commas for multiple streams.  AC3 ignores this option, '
        'but it must be specified if using multiple audio streams.  Example '
        '(from AUDIO example) 128,384,192,auto.  Default 160 for all streams.',
        default='160')
    self.audio_mixdown = options.StringOption(
        long='--mixdown', short='-6', description='Surround sound downmixing '
        'format (mono/stereo/dpl1/dpl2/6ch/auto), separated by commas for '
        'multiple streams.  AC3 ignores this option, but it must be specified '
        'if using multiple audio streams.  Example (from AUDIO example) '
        '6ch,dpl2,dpl1,auto.  Default dpl2 (Dolby Pro-Logic 2).  '
        'http://trac.handbrake.fr/wiki/SurroundSoundGuide.', default='dpl2')
    self.audio_sample_rate = options.StringOption(
        long='--arate', short='-R', description='Set audio samplerate in '
        'kilohertz (22.05/24/32/44.1/48) plus any other values supported by '
        'audio encoder.  For multiple audio stream, separated by commas.  '
        'Example (from AUDIO example) 24,44.1,44.1,48.  AC3 ignores this '
        'option, but must be specified if using multiple streams.  Default rate'
        ' is same as source, or best alternative rate.', default=None)
    self.audio_dynamic_range_compression = options.StringOption(
        long='--drc', short='-D', description='Dynamic range compression, '
        'making soft sounds louder without changing louder sounds.  From 1.0 '
        '(off) to 4.0 (max loudest for all sounds).  Effective settings are '
        'between 1.5-2.5.  Can be used for multiple streams, but must be comma '
        'separated.  AC3 ignores this option, but must be specified in multiple'
        ' streams.  Example (from AUDIO example) 1.5,1.5,1.5,1.0.  Default 1.0 '
        '(autodetect).', default=None)
    self.audio_mp4_track_name = options.StringOption(
        long='--aname', short='-A', description='Audio track name, separated by'
        ' commas for multiple tracks.  If not mp4 file, this option is ignored.'
        "  Example (from AUDIO example) Main Track - AAC','Main Track - AC3',"
        "'Commentary','Extras'.  Must be used for AppleTV encodes with multiple"
        ' streams.  Default none.', default=None)
    self.width = options.IntegerOption(
        long='--width', short='-w', description='Set picture width in pixels, '
        '720 widescreen, 640 fullscreen.  If no HEIGHT is specified, it will '
        'calculate a height to preserve aspect ratio.  Default autodetect ratio'
        ' and use appropriate width.', default=None)
    self.height = options.IntegerOption(
        long='--height', short='-l', description='Set picture height in pixels.'
        '  If no WIDTH is specified, it will calculate a width to preserve '
        'aspect ratio.  Default autodetect ratio and use appropriate height.',
        default=None)
    self.crop = options.StringOption(
        long='--crop', short='--crop', description='Set cropping values '
        '([Top:Bottom:Left:Right],autocrop) in pixels.  Autocrap will '
        'automatically detect and remove bars.  Default autocrop.',
        default=None)
    self.max_height = options.IntegerOption(
        long='--maxHeight', short='-Y', description='Set maximum allowed height'
        ' in pixels, anything over will be scaled with width to fit and '
        'preserve aspect ratio.  Default no max.', default=None)
    self.max_width = options.IntegerOption(
        long='--maxWidth', short='-X', description='Set maximum allowed width '
        'in pixels, anythin over will be scaled with height to fit and preserve'
        ' aspect ratio.  Default no max.', default=None)
    self.strict_anamorphic = options.BooleanOption(
        long='--pixelratio', short='-p', description='Store pixel aspect ratio '
        'in video stream (strict anamorphic).  Should use this option for best '
        'encoded videos.  http://trac.handbrake.fr/wiki/AnamorphicGuide.  '
        'Default no strict.  NO OPTIONS.', default=None)
    self.loose_anamorphic = options.StringOption(
        long='--loosePixelratio', short='-P', description='Divides dimensions '
        'cleanly by 16, and optionally the pixel ratio to use.  Useful for x264'
        ' encoding.  Allows scaling down by giving WIDTH.  Example 8 or '
        '8:1.33:1.  http://trac.handbrake.fr/wiki/AnamorphicGuide#loose.  '
        'http://trac.handbrake.fr/wiki/AnamorphicGuide#itu.  Default 16:auto.',
        default='16:auto')
    self.color_matrix = options.SetOption(
        long='--color-matrix', short='-M', description='Set color space for '
        'video (601,709).  601 - standard definition, 709 - high definition.  '
        'Default set by resolution.', set=[601, 709], default=601)
    self.filter_deinterlace = options.StringOption(
        long='--deinterlace', short='-d', description='Deinterlace video with '
        'yadif/mcdeint filter.  Can specify by speed (fast,slow,slower) or '
        'filter specification <YM:FD:MM:QP>.  It is almost always better to use'
        ' FILTER_DECOMB.  http://trac.handbrake.fr/wiki/DeinterlacingGuide.  '
        'Default 0:-1:-1:1 (fast).', default='0:-1:-1:1')
    self.filter_decomb = options.StringOption(
        long='--decomb', short='-5', description='Selectively deinterlace when '
        "combing is detected.  By default runs as 'slower' option for "
        'deinterlace (fast,slow,slower).  Can use filter specification as well '
        '<MO:ME:MT:ST:BT:BX:BY>.  http://trac.handbrake.fr/wiki/Decomb.  '
        'Default None.', default=None)
    self.filter_detelecine = options.StringOption(
        long='--detelecine', short='-9', description='Inverse telecine (ivtc) '
        'pullup filter (<L:R:T:B:SB:MP>).  Restores video to progressive if '
        'framerate different than source.  Drops duplicate frames to restore '
        'the pre-telecine framerate, unless you specify a constant framerate '
        'VIDEO_FRAME_RATE.  Default 1:1:4:4:0:0.', default='1:1:4:4:0:0')
    self.filter_denoise = options.StringOption(
        long='--denoise', short='-8', description='Denoise video with hqdn3d '
        'filter (<SL:SC:TL:TC>) or by strength (weak,medium,strong).  Default '
        '4:3:6:4.5 (between medium and strong).', default='4:3:6:4.5')
    self.filter_deblock = options.StringOption(
        long='--deblock', short='-7', description='Deblock video with pp7 '
        'filter.  From 1-10, or <QP:M>.  1 very little deblocking, 10 may be '
        'too blurry.  Default 5 (5:2).', default='5')
    self.filter_grayscale = options.BooleanOption(
        long='--grayscale', short='-g', description='Enable Grayscale encoding.'
        '  Useful to encode black and white videos in true black and white.  '
        'Default off.  NO OPTIONS.', default=None)
    self.subtitles = options.RangeOption(
        long='--subtitle', short='-s', description='Select subtitle track to '
        'use, From 1-X.  This will force handbrake to hard-burn the subtitles '
        'into the movie, you will NOT be able to turn them off.  Default no '
        'subtitles.', low=1, high=self.max_size, default=None)
    self.subtitles_scan = options.BooleanOption(
        long='--subtitle-scan', short='-U', description='Scan for subtitles in '
        'an extra 1st pass, and choose the one that is only used 10 percent of '
        'the time or less.  This should locate subtitles for short foreign '
        'language segments.  Should be used with SUBTITLES_IF_FORCED.  Default '
        'no scan.  NO OPTIONS.', default=None)
    self.subtitles_if_forced = options.BooleanOption(
        long='--subtitle-forced', short='-F', description='Only display '
        'subtitles from the selected stream if the subtitle has the forced flag'
        ' set.  May be used in conjunction with SUBTITLES_SCAN to auto-select a'
        ' stream if it contains forced subtitles.  Default no forced subtitles.'
        '  NO OPTIONS.', default=None)
    self.subtitles_native_language = options.StringOption(
        long='--native-language', short='-N', description='Use subtitles in '
        'specified languages, if audio differs from your native language.  Can '
        'specify any ISO639-2 language, example eng.  Full list: '
        'http://www.loc.gov/standards/iso639-2/php/code_list.php.  Default '
        'none.', default=None)
    self.all = [
        self.general_update, self.general_verbose, self.general_cpu,
        self.general_preset, self.file_input, self.file_title,
        self.file_longest_title, self.file_chapters, self.file_output,
        self.file_format, self.file_markers, self.file_large_file_support,
        self.file_mp4_web_optimize, self.file_mp4_ipod_atom, self.video_encoder,
        self.video_x264_opts, self.video_two_pass,
        self.video_x264_turbo_first_pass, self.video_frame_rate,
        self.video_quality, self.video_x264_constant_quantizer,
        self.video_target_size, self.video_bitrate, self.audio,
        self.audio_encoder, self.audio_bitrate, self.audio_mixdown,
        self.audio_sample_rate, self.audio_dynamic_range_compression,
        self.audio_mp4_track_name, self.width, self.height, self.crop,
        self.max_height, self.max_width, self.strict_anamorphic,
        self.loose_anamorphic, self.color_matrix, self.filter_deinterlace,
        self.filter_decomb, self.filter_detelecine, self.filter_denoise,
        self.filter_deblock, self.filter_grayscale, self.subtitles,
        self.subtitles_scan, self.subtitles_if_forced,
        self.subtitles_native_language]

