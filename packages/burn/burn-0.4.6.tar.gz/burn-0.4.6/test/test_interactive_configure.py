# -*- coding: utf-8 -*-

# test/test_interactive_configure.py
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

""" Unit test module for ‘interactive_configure’ module.
    """

import sys
import textwrap
import optparse
import re
import pprint
import difflib

import nose.tools
import minimock

from burnlib import interactive_configure
import burnlib.version


def setup_option_parser_fixtures(testcase):
    """ Set up common ‘OptionParser’ fixtures for test cases. """
    testcase.mock_tracker = minimock.TraceTracker()

    testcase.test_instance = interactive_configure.OptionParser()

    minimock.mock(
        "interactive_configure.OptionParser.error",
        tracker=testcase.mock_tracker)


class OptionParser_TestCase(object):
    """ Test cases for program ‘OptionParser’ class. """

    def setup(self):
        """ Set up test fixtures. """
        test_prog_name = "worple"
        minimock.mock(
            "sys.argv",
            mock_obj=[test_prog_name])

        setup_option_parser_fixtures(self)

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_is_option_parser_instance(self):
        """ Should be an instance of standard OptionParser class. """
        expect_superclass = optparse.OptionParser
        nose.tools.assert_true(
            isinstance(self.test_instance, expect_superclass))

    def test_has_default_program_name(self):
        """ Should have default program name. """
        expect_result = interactive_configure.OptionParser.default_program_name
        result = self.test_instance.get_prog_name()
        nose.tools.assert_equal(expect_result, result)

    def test_has_default_usage_text(self):
        """ Should have default usage text. """
        expect_usage = (
            "Usage: %(default_usage)s\n" % vars(interactive_configure.OptionParser))
        program_name = interactive_configure.OptionParser.default_program_name
        expect_result = re.sub('%prog', program_name, expect_usage)
        result = self.test_instance.get_usage()
        nose.tools.assert_equal(expect_result, result)

    def test_has_expected_version(self):
        """ Should have expected version string. """
        expect_result = burnlib.version.version
        result = self.test_instance.get_version()
        nose.tools.assert_equal(expect_result, result)

    def test_has_default_description(self):
        """ Should have default summary description. """
        expect_result = interactive_configure.OptionParser.default_description
        result = self.test_instance.get_description()
        nose.tools.assert_equal(expect_result, result)

    def test_has_default_epilog(self):
        """ Should have default help epilogue text. """
        expect_result = interactive_configure.OptionParser.default_epilog
        result = self.test_instance.epilog
        nose.tools.assert_equal(expect_result, result)

    def check_has_expected_option(self, expect_option):
        def get_option_attrs(option):
            attrs = dict(
                (name, getattr(option, name))
                for name in [
                    '_short_opts', '_long_opts',
                    'action', 'type', 'dest', 'default',
                    'nargs', 'const', 'choices',
                    'metavar'])
            return attrs
        expect_option_attrs = get_option_attrs(expect_option)
        option_string = expect_option._long_opts[0]
        nose.tools.assert_true(
            self.test_instance.has_option(option_string),
            "option not found: %(option_string)r" % vars())
        option = self.test_instance.get_option(option_string)
        option_attrs = get_option_attrs(option)
        nose.tools.assert_equal(
            expect_option_attrs, option_attrs,
            "\n".join(difflib.unified_diff(
                pprint.saferepr(expect_option_attrs).split(),
                pprint.saferepr(option_attrs).split()))
            )

    def test_has_expected_options(self):
        """ Should have expected options. """
        options = [
            optparse.Option(
                "-t", "--template-file",
                action='store', type='string', dest='template_file_path',
                default="/usr/share/burn/example/burn.conf",
                metavar="PATH"),
            optparse.Option(
                "-o", "--output-file",
                action='store', type='string', dest='output_file_path',
                default="burn.conf.new",
                metavar="PATH"),
            ]
        for option in options:
            yield (
                self.check_has_expected_option,
                option)


class OptionParser_check_values_TestCase(object):
    """ Test cases for ‘OptionParser.check_values’ method. """

    mock_option_values = minimock.Mock("Values")

    valid_scenarios = [
        ('no args', {
            'in_params': {'values': mock_option_values, 'args': []},
            }),
        ]

    invalid_scenarios = [
        ('one arg', {
            'in_params': {'values': mock_option_values, 'args': ["foo"]},
            'message': "unexpected arguments: foo",
            }),
        ('two args', {
            'in_params': {'values': mock_option_values, 'args': ["foo", "bar"]},
            'message': "unexpected arguments: foo bar",
            }),
        ]

    def setup(self):
        """ Set up test fixtures. """
        setup_option_parser_fixtures(self)

        for (name, scenario) in self.valid_scenarios:
            scenario['expect_result'] = (
                scenario['in_params']['values'], scenario['in_params']['args'])

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_requests_error_when_invalid_arg_count(self):
        """ Should request parser error when invalid argument count. """
        for (name, scenario) in self.invalid_scenarios:
            yield (
                self.check_requests_error_when_invalid_arg_count,
                scenario)

    def check_requests_error_when_invalid_arg_count(self, scenario):
        in_params = scenario['in_params']
        expect_error_message = scenario['message']
        expect_mock_output = textwrap.dedent("""\
            ...Called interactive_configure.OptionParser.error(%(expect_error_message)r)
            """) % vars()
        self.test_instance.check_values(**in_params)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_returns_expected_options_and_args(self):
        """ Should return expected ‘options’ and ‘args’. """
        for (name, scenario) in self.valid_scenarios:
            yield (
                self.check_returns_expected_options_and_args,
                scenario)

    def check_returns_expected_options_and_args(self, scenario):
        in_params = scenario['in_params']
        expect_result = scenario['expect_result']
        result = self.test_instance.check_values(**in_params)
        nose.tools.assert_equal(expect_result, result)


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
