# -*- coding: utf-8 -*-

# burnlib/__init__.py
#
# Copyright © 2009 Ben Finney <ben+python@benfinney.id.au>.
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

# The module docstring is used as input to distutils for the short and
# long descriptions. Due to <URL:http://bugs.python.org/issue2562>,
# distutils in Python 2.5 cannot handle any encoding other than ASCII;
# once Python 2.5 is no longer required for building the distribution,
# this docstring can be properly encoded in full UTF-8.

""" Command-line tool for writing optical media.

    'burn' is a command-line tool to create audio discs from MP3, Ogg
    Vorbis, or WAV files, to backup data files, to create discs from
    ISO-9660 images, and to copy discs on-the-fly. It performs any of
    its functions in a single command, without requiring preparatory
    filesystem creation, etc.

    The program can compute if there is necessary free space for
    temporary files (images and audio files), warn if size is bigger
    than disc capacity, and manage multisession discs.

    """


_url = "http://www.bigpaul.org/burn/"
