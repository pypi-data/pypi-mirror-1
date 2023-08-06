# -*- coding: utf-8 -*-

# test/test_audio.py
# Part of ‘burn’, a tool for writing optical media.
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

""" Unit test module for ‘audio’ module.
    """

import subprocess
import textwrap

import nose.tools
import minimock

from burnlib import audio


def test_compute_duration_returns_expected_output():
    """ Should return expected output for specified seconds value. """
    scenarios = [
        ('0:00', {'seconds': 0, 'result': "0:00"}),
        ('0:01', {'seconds': 1, 'result': "0:01"}),
        ('0:07', {'seconds': 7, 'result': "0:07"}),
        ('0:20', {'seconds': 20, 'result': "0:20"}),
        ('0:58', {'seconds': 58, 'result': "0:58"}),
        ('0:59', {'seconds': 59, 'result': "0:59"}),
        ('1:00', {'seconds': 60, 'result': "1:00"}),
        ('1:01', {'seconds': 61, 'result': "1:01"}),
        ('1:42', {'seconds': 102, 'result': "1:42"}),
        ('27:19', {'seconds': 1639, 'result': "27:19"}),
        ('59:59', {'seconds': 3599, 'result': "59:59"}),
        ('1:00:00', {'seconds': 3600, 'result': "1:00:00"}),
        ('1:00:01', {'seconds': 3601, 'result': "1:00:01"}),
        ('7:05:36', {'seconds': 25536, 'result': "7:05:36"}),
        ]
    for (name, scenario) in scenarios:
        yield (
            check_compute_duration_output,
            scenario['seconds'], scenario['result'])

def check_compute_duration_output(seconds, expect_result):
    result = audio.compute_duration(seconds)
    nose.tools.assert_equal(expect_result, result)


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
