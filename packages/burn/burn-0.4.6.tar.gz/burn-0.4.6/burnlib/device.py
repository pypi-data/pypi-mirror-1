# -*- coding: utf-8 -*-

# burnlib/device.py
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

""" Functionality for working with optical media devices.
    """

import subprocess


def device_list_output():
    """ Return output of query to optical media devices. """
    process = subprocess.Popen(
        ["wodim", "-devices"],
        stdout=subprocess.PIPE)
    process_stdout = process.communicate()[0]
    return process_stdout


def bus_list_output():
    """ Return output of query to optical media device bus. """
    process = subprocess.Popen(
        ["wodim", "-scanbus"],
        stdout=subprocess.PIPE)
    process_stdout = process.communicate()[0]
    return process_stdout


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
