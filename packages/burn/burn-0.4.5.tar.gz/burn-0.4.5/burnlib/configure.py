# -*- coding: utf-8 -*-

# burnlib/configure.py
#
# Copyright © 2009 Ben Finney <ben+python@benfinney.id.au>.
# Copyright © 2004–2009 Gaetano Paolone <bigpaul@hacknight.org>.
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

""" Configuration options for ‘burn’.

    config
        The configuration object for parsing config files.

    config_defaults
        Default configuration options.

    config_file_paths
        List of config file paths that will be used, in order.

    read_from_files(paths)
        Sets up the config object with options read from config files.

    """

import sys
import os
import os.path
import gettext
import ConfigParser


#gettext
gettext.bindtextdomain('burn_configure', '/usr/share/locale/it/LC_MESSAGES/')
gettext.textdomain('burn_configure')
_ = gettext.gettext

config_file_paths = [
    os.path.join('/', 'etc', 'burn.conf'),
    os.path.join(os.environ['HOME'], '.burnrc'),
    ]

config_defaults = {
    'ask_root': "yes",
    'external_decoding': "no",
    'pause': "yes",

    'wodim': "/usr/bin/wodim",
    'cdrdao': "/usr/bin/cdrdao",
    'genisoimage': "/usr/bin/genisoimage",
    'mp3_decoder': "/usr/bin/mpg321",
    'mp3_decoder_option': "-q -w",
    'ogg_decoder': "/usr/bin/ogg123",
    'ogg_decoder_option': "-q -d wav -f",

    'tempdir': "/tmp/",
    'image': "burn_image.iso",
    'windows_read': "yes",
    'mount_dir': "/mnt/",

    'device': "/dev/cdrom",
    'speed': "4",
    'driver': "generic-mmc",
    'burnfree': "yes",

    'media-check': "no",
    'size': "700",
    }

config = ConfigParser.SafeConfigParser(config_defaults)


def read_from_files(parser=None, paths=None):
    """ Read the configuration from files into the config object.

        The ConfigParser behaviour is to silently ignore those paths
        that do not exist, allowing a cascade of potential config
        files to be read in sequence, each one overriding any previous
        settings.

        """

    if parser is None:
        parser = config
    if paths is None:
        paths = config_file_paths
    parser.read(paths)


def read_from_template(parser, template_path):
    """ Read the configuration from specified template file.
        """
    template_file = open(template_path)
    parser.readfp(template_file)


def make_config_from_template(template_path):
    """ Make a config object from specified template file.

        If an error occurs reading the configuration template, exit
        with an error message.

        """

    parser = ConfigParser.SafeConfigParser(config_defaults)
    try:
        read_from_template(parser, template_path)
    except EnvironmentError, exc:
        message = _(
            "Failed to read template configuration file: %(exc)s\n"
            ) % vars()
        sys.exit(message)

    return parser


def write_to_file(parser, path):
    """ Write configuration to specified path.

        If an error occurs opening or writing the configuration file,
        exit with an error message.

        """

    try:
        config_file = open(path, 'w')
        parser.write(config_file)
    except EnvironmentError, exc:
        message = _(
            "Failed to write configuration file: %(exc)s\n"
            ) % vars()
        sys.exit(message)


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
