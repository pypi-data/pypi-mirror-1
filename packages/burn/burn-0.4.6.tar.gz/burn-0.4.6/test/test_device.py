# -*- coding: utf-8 -*-

# test/test_device.py
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

""" Unit test module for ‘device’ module.
    """

import os
import subprocess
import textwrap

import nose.tools
import minimock

from burnlib import device


def setup_popen_fixtures(testcase):
    """ Set up common fixtures for ‘subprocess.Popen’ test cases. """
    testcase.mock_tracker = minimock.TraceTracker()

    testcase.mock_popen = minimock.Mock(
        "Popen",
        tracker=testcase.mock_tracker)
    testcase.mock_popen.communicate.mock_returns = (None, None)
    minimock.mock(
        "subprocess.Popen",
        returns=testcase.mock_popen,
        tracker=testcase.mock_tracker)


class wodim_query_TestCase(object):
    """ Test cases for functions that query ‘wodim’ command. """

    test_func = NotImplemented

    def setup(self):
        """ Set up test fixtures. """
        setup_popen_fixtures(self)

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def check_creates_expected_popen(self):
        """ Should create a Popen instance with expected arguments. """
        expect_command_args = self.command_args
        expect_popen_stdout = subprocess.PIPE
        expect_mock_output = textwrap.dedent("""\
            Called subprocess.Popen(
                %(expect_command_args)r,
                stdout=%(expect_popen_stdout)r
                )
            ...
            """) % vars()
        func = self.__class__.test_func
        func()
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def check_communicates_with_popen_pipe(self):
        """ Should communicate with the Popen instance's pipe. """
        expect_mock_output = textwrap.dedent("""\
            ...
            Called Popen.communicate()
            """) % vars()
        func = self.__class__.test_func
        func()
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def check_returns_popen_pipe_output(self):
        """ Should return the output from the Popen instance's stdout. """
        test_output = "foo\nbar"
        self.mock_popen.communicate.mock_returns = (test_output, None)
        expect_output = test_output
        func = self.__class__.test_func
        result = func()
        nose.tools.assert_equal(expect_output, result)


class device_list_output_TestCase(wodim_query_TestCase):
    """ Test cases for ‘device_list_output’ function. """

    test_func = staticmethod(device.device_list_output)

    command_args = ["wodim", "-devices"]

    def test_creates_expected_popen(self):
        self.check_creates_expected_popen()

    def test_communicates_with_popen_pipe(self):
        self.check_communicates_with_popen_pipe()

    def test_returns_popen_pipe_output(self):
        self.check_returns_popen_pipe_output()


class bus_list_output_TestCase(wodim_query_TestCase):
    """ Test cases for ‘bus_list_output’ function. """

    test_func = staticmethod(device.bus_list_output)

    command_args = ["wodim", "-scanbus"]

    def test_creates_expected_popen(self):
        self.check_creates_expected_popen()

    def test_communicates_with_popen_pipe(self):
        self.check_communicates_with_popen_pipe()

    def test_returns_popen_pipe_output(self):
        self.check_returns_popen_pipe_output()


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
