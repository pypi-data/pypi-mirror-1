# -*- coding: utf-8 -*-

# burnlib/audio.py
#
# Copyright © 2009 Ben Finney <ben+python@benfinney.id.au>.
# Copyright © 2003–2009 Gaetano Paolone <bigpaul@hacknight.org>.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.

""" Functionality for working with audio files.
    """

import os.path
import ogg.vorbis
import eyeD3
import mad


class FileInfo:
    """ Grab as much info as you can from the file given.

        Reads time, tags, title, artist, and more from file.

        """

    def __init__(self, fullpath):
        """ Set up the file information from the specified path. """
        base, ext = os.path.splitext(fullpath)
        if ext.lower() == '.ogg':
            fileinfo = OggInfo(fullpath)
            self.__dict__.update(fileinfo.__dict__)
            self.fileinfo = fileinfo
        else:
            tag = eyeD3.Tag()
            tag.link(fullpath)
            self.artist = tag.getArtist()
            self.title = tag.getTitle()
            self.album = tag.getAlbum()
            fileinfo = mad.MadFile(fullpath)
            self.total_time = fileinfo.total_time() / 1024
            self.bitrate = fileinfo.bitrate() / 1000
            self.fileinfo = fileinfo

        self.duration = compute_duration(self.total_time)

    def read(self):
        """ Read and return the file information. """
        return self.fileinfo.read()


class OggInfo:
    """Extra information about an Ogg Vorbis file.
    Uses ogg-python and vorbis-python from http://www.duke.edu/~ahc4/pyogg/.
    Patch from Justin Erenkrantz <justin@erenkrantz.com>
    """

    def __init__(self, name):

        # Setup the defaults
        self.valid = 0
        self.total_time = 0
        self.samplerate = 'unkown'
        self.bitrate = 'unkown'
        self.mode = ''
        self.mode_extension = ''
        self.title = ''
        self.artist = ''
        self.album = ''
        self.year = ''
        self.genre = ''
        self.vendor = ''
        self.track = ''
        self.comment = ''
        self.transcoded = ''

        # Generic File Info
        fileogg = ogg.vorbis.VorbisFile(name)
        ogg_comment = fileogg.comment()
        ogg_info = fileogg.info()
        self.fileogg = fileogg

        # According to the docs, -1 means the current bitstream
        self.samplerate = ogg_info.rate
        self.total_time = fileogg.time_total(-1)
        self.bitrate = fileogg.bitrate(-1) / 1000
        self.filesize = fileogg.raw_total(-1)/1024/1024

        # recognized_comments = ('Artist', 'Album', 'Title', 'Version',
        #                        'Organization', 'Genre', 'Description',
        #                        'Date', 'Location', 'Copyright', 'Vendor')
        for key, val in ogg_comment.items():
            if key == 'TITLE':
                self.title = val
            elif key == 'ARTIST':
                self.artist = val
            elif key == 'ALBUM':
                self.album = val
            elif key == 'DATE':
                self.year = val
            elif key == 'GENRE':
                self.genre = val
            elif key == 'VENDOR':
                self.vendor = val
            elif key == 'TRACKNUMBER':
                self.track = val
            elif key == 'COMMENT':
                self.comment = val
            elif key == 'TRANSCODED':
                self.transcoded = val
        self.valid = 1

    def read(self):
        """ Read and return the file information. """
        return self.fileogg.read()


def file_duration(audio_file):
    """ Return audio duration in seconds from specified audio file. """

    seconds = 0
    if os.path.exists(audio_file) and os.path.isfile(audio_file):
        info = FileInfo(audio_file)
        seconds = seconds + int(info.total_time)
        return seconds
    else:
        return -1


def compute_duration(seconds):
    """ Return duration string for duration in seconds.

        Will return the appropriate format for the duration:

        * "H:MM:SS" for durations one hour or more
        * "M:SS" for durations one minute or more
        * "0:SS" for durations less than one minute

        """

    seconds_per_hour = 3600
    minutes_per_hour = 60
    seconds_per_minute = 60
    if seconds >= seconds_per_hour:
        duration = '%d:%02d:%02d' % (
            int(seconds / seconds_per_hour),
            int(seconds / seconds_per_minute) % minutes_per_hour,
            int(seconds) % seconds_per_minute)
    elif seconds >= seconds_per_minute:
        duration = '%d:%02d' % (
            int(seconds / seconds_per_minute),
            int(seconds) % seconds_per_minute)
    else:
        duration ='0:%02d' % int(seconds)
    return duration


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
