# -*- coding: utf-8 -*-

# test/test_configure.py
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

""" Unit test module for ‘configure’ module.
    """

import __builtin__
import doctest
import ConfigParser
import textwrap
import functools
import operator
import tempfile
from StringIO import StringIO
import errno

import nose.tools
import minimock

from burnlib import configure
import burnlib.version


class config_file_paths_TestCase(object):
    """ Test cases for ‘config_file_paths’ object. """

    def test_items_are_strings(self):
        """ Every item in the list should be a string. """
        string_items = [
            item for item in configure.config_file_paths
            if isinstance(item, basestring)]
        nose.tools.assert_equal(string_items, configure.config_file_paths)


class config_TestCase(object):
    """ Test cases for ‘config’ object. """

    def test_config_is_safe_config_parser(self):
        """ Should be a SafeConfigParser instance. """
        nose.tools.assert_true(
            isinstance(configure.config, ConfigParser.SafeConfigParser))

    def test_config_has_expected_defaults(self):
        """ Should have expected default settings. """
        expect_defaults = {
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
        defaults = configure.config.defaults()
        nose.tools.assert_equal(expect_defaults, defaults)


def make_mock_config_parser(name, instance, tracker, defaults=None):
    """ Make a mock SafeConfigParser object. """

    if instance is None:
        instance = minimock.Mock(name, tracker=tracker)

    instance.defaults.mock_returns = defaults

    def mock_parser_read(instance, paths):
        instance._paths_read = paths
        return paths
    instance.read.mock_returns_func = functools.partial(
        mock_parser_read, instance)

    return instance


def setup_config_parser_fixtures(testcase):
    """ Set up common ConfigParser fixtures for test cases. """
    testcase.mock_tracker = minimock.TraceTracker()

    testcase.mock_config_defaults = {
        'foo': "spam",
        'bar': "eggs",
        }

    minimock.mock(
        "configure.config_defaults",
        mock_obj=testcase.mock_config_defaults)

    testcase.mock_parser = make_mock_config_parser(
        name="configure.config", instance=None,
        defaults=configure.config_defaults,
        tracker=testcase.mock_tracker)

    minimock.mock(
        "ConfigParser.SafeConfigParser",
        returns_func=functools.partial(
            make_mock_config_parser,
            "ConfigParser.SafeConfigParser", testcase.mock_parser,
            testcase.mock_tracker),
        tracker=testcase.mock_tracker)

    minimock.mock(
        "configure.config",
        mock_obj=ConfigParser.SafeConfigParser(
            configure.config_defaults),
        tracker=testcase.mock_tracker)


class read_from_files_TestCase(object):
    """ Test cases for ‘read_from_files’ function. """

    def setup(self):
        """ Set up test fixtures. """
        setup_config_parser_fixtures(self)

        self.mock_config_file_paths = ["foo.conf", "bar.conf", "baz.conf"]
        minimock.mock(
            "configure.config_file_paths",
            mock_obj=self.mock_config_file_paths)

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_reads_config_files_to_module_config(self):
        """ Should read the default config files to module config object. """
        expect_file_paths = self.mock_config_file_paths
        configure.read_from_files()
        paths_read = self.mock_parser._paths_read
        nose.tools.assert_equal(expect_file_paths, paths_read)

    def test_reads_specified_config_files_to_module_config(self):
        """ Should read the specified config files to module config object. """
        test_config_paths = ["wibble", "wobble"]
        args = {
            'paths': test_config_paths,
            }
        expect_file_paths = test_config_paths
        configure.read_from_files(**args)
        paths_read = self.mock_parser._paths_read
        nose.tools.assert_equal(expect_file_paths, paths_read)

    def test_reads_config_files_to_specified_config(self):
        """ Should read the default config files to specified config. """
        test_parser = make_mock_config_parser(
            "custom_config", instance=None,
            tracker=self.mock_tracker)
        args = {
            'parser': test_parser,
            }
        expect_file_paths = self.mock_config_file_paths
        configure.read_from_files(**args)
        paths_read = test_parser._paths_read
        nose.tools.assert_equal(expect_file_paths, paths_read)

    def test_reads_specified_config_files_to_specified_config(self):
        """ Should read the specified config files to specified config. """
        test_parser = make_mock_config_parser(
            "custom_config", instance=None,
            tracker=self.mock_tracker)
        test_config_paths = ["wibble", "wobble"]
        args = {
            'parser': test_parser,
            'paths': test_config_paths,
            }
        expect_file_paths = test_config_paths
        configure.read_from_files(**args)
        paths_read = test_parser._paths_read
        nose.tools.assert_equal(expect_file_paths, paths_read)


def setup_config_file_fixtures(testcase):
    """ Set up common fixtures for config file test cases. """

    testcase.mock_config_file = StringIO()

    def mock_config_open(testcase, filename, mode, buffering):
        result = testcase.mock_config_file
        return result

    testcase.config_open_func = functools.partial(
        mock_config_open,
        testcase)

    testcase.test_config_file_path = tempfile.mktemp()

    def mock_open(testcase, filename, mode='r', buffering=None):
        if filename == testcase.test_config_file_path:
            result = testcase.config_open_func(filename, mode, buffering)
        else:
            result = StringIO()
        return result

    minimock.mock(
        "__builtin__.open",
        returns_func=functools.partial(mock_open, testcase),
        tracker=testcase.mock_tracker)


class read_from_template_TestCase(object):
    """ Test cases for ‘read_from_template’ function. """

    def setup(self):
        """ Set up test fixtures. """
        setup_config_parser_fixtures(self)

        self.test_parser = make_mock_config_parser(
            "custom_config", instance=None,
            tracker=self.mock_tracker)

        setup_config_file_fixtures(self)

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_reads_template_to_module_config(self):
        """ Should read the template config to module config object. """
        args = {
            'parser': self.test_parser,
            'template_path': self.test_config_file_path,
            }
        expect_mock_output = textwrap.dedent("""\
            ...
            Called __builtin__.open(%(test_config_file_path)r)
            Called custom_config.readfp(%(mock_config_file)r)
            """) % vars(self)
        configure.read_from_template(**args)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))


def assert_checker_match(want, got, message=None):
    """ Assert the wanted output matches the got output. """
    checker = doctest.OutputChecker()
    want = textwrap.dedent(want)
    source = ""
    example = doctest.Example(source, want)
    got = textwrap.dedent(got)
    checker_optionflags = reduce(operator.or_, [
        doctest.ELLIPSIS,
        ])
    if not checker.check_output(want, got, checker_optionflags):
        if message is None:
            diff = checker.output_difference(
                example, got, checker_optionflags)
            message = "\n".join([
                "Output received did not match expected output",
                "%(diff)s",
                ]) % vars()
        raise AssertionError(message)


class make_config_from_template_TestCase(object):
    """ Test cases for ‘make_config_from_template’ function. """

    def setup(self):
        """ Set up test fixtures. """
        setup_config_parser_fixtures(self)

        setup_config_file_fixtures(self)

        minimock.mock(
            "configure.read_from_template",
            tracker=self.mock_tracker)

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_creates_parser_with_defaults(self):
        """ Should create a parser with module defaults. """
        args = {
            'template_path': self.test_config_file_path,
            }
        expect_defaults = self.mock_config_defaults
        parser = configure.make_config_from_template(**args)
        defaults = parser.defaults()
        nose.tools.assert_equal(expect_defaults, defaults)

    def test_populates_parser_from_template_file(self):
        """ Should populate the parser from specified template file. """
        args = {
            'template_path': self.test_config_file_path,
            }
        expect_mock_output = textwrap.dedent("""\
            ...
            Called configure.read_from_template(
                %(mock_parser)r,
                %(test_config_file_path)r)
            """) % vars(self)
        configure.make_config_from_template(**args)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_exits_with_error_when_error_from_read_from_template(self):
        """ When error from ‘read_from_template’, should exit with error. """
        scenarios = [
            ('OSError', {
                'error_instance': OSError(errno.EPERM, "Permission denied"),
                }),
            ('IOError', {
                'error_instance': IOError(errno.ENOENT, "No such file"),
                }),
            ]

        for (name, scenario) in scenarios:
            yield (
                self.check_exits_with_error,
                scenario['error_instance'])

    def check_exits_with_error(self, error_instance):
        args = {
            'template_path': self.test_config_file_path,
            }
        configure.read_from_template.mock_raises = error_instance
        error_message = str(error_instance)
        expect_exc_class = SystemExit
        expect_exc_message = textwrap.dedent("""\
            ...: %(error_message)s
            """) % vars()
        try:
            configure.make_config_from_template(**args)
        except expect_exc_class, exc:
            pass
        else:
            raise AssertionError("%(expect_exc_class)r not raised")
        assert_checker_match(expect_exc_message, str(exc))


class write_to_file_TestCase(object):
    """ Test cases for ‘write_to_file’ function. """

    def setup(self):
        """ Set up test fixtures. """
        setup_config_parser_fixtures(self)

        setup_config_file_fixtures(self)

        self.mock_tracker.clear()

        self.test_args = {
            'parser': self.mock_parser,
            'path': self.test_config_file_path,
            }

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_opens_specified_file_in_write_mode(self):
        """ Should open specified file in write mode. """
        expect_path = self.test_config_file_path
        expect_mode = 'w'
        expect_mock_output = textwrap.dedent("""\
            Called __builtin__.open(
                %(expect_path)r,
                %(expect_mode)r)
            ...
            """) % vars()
        configure.write_to_file(**self.test_args)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_exits_with_error_when_error_from_open(self):
        """ When error from ‘open’, should exit with error. """
        scenarios = [
            ('OSError', {
                'error_instance': OSError(errno.EPERM, "Permission denied"),
                }),
            ('IOError', {
                'error_instance': IOError(errno.ENOENT, "No such file"),
                }),
            ]

        for (name, scenario) in scenarios:
            yield (
                self.check_exits_with_error_when_error_from_open,
                scenario['error_instance'])

    def check_exits_with_error_when_error_from_open(self, error_instance):
        __builtin__.open.mock_raises = error_instance
        error_message = str(error_instance)
        expect_exc_class = SystemExit
        expect_exc_message = textwrap.dedent("""\
            ...: %(error_message)s
            """) % vars()
        try:
            configure.write_to_file(**self.test_args)
        except expect_exc_class, exc:
            pass
        else:
            raise AssertionError("%(expect_exc_class)r not raised")
        assert_checker_match(expect_exc_message, str(exc))

    def test_writes_specified_config_to_file(self):
        """ Should write the specified config to the file. """
        expect_file = self.mock_config_file
        expect_mock_output = textwrap.dedent("""\
            ...
            Called configure.config.write(%(expect_file)r)
            """) % vars()
        configure.write_to_file(**self.test_args)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_exits_with_error_when_error_from_config_write(self):
        """ When error from config ‘write’, should exit with error. """
        scenarios = [
            ('OSError', {
                'error_instance': OSError(errno.EINVAL, "Invalid entry"),
                }),
            ('IOError', {
                'error_instance': IOError(errno.ENOSPC, "No space left"),
                }),
            ]

        for (name, scenario) in scenarios:
            yield (
                self.check_exits_with_error_when_error_from_config_write,
                scenario['error_instance'])

    def check_exits_with_error_when_error_from_config_write(
        self, error_instance):
        self.mock_parser.write.mock_raises = error_instance
        error_message = str(error_instance)
        expect_exc_class = SystemExit
        expect_exc_message = textwrap.dedent("""\
            ...: %(error_message)s
            """) % vars()
        try:
            configure.write_to_file(**self.test_args)
        except expect_exc_class, exc:
            pass
        else:
            raise AssertionError("%(expect_exc_class)r not raised")
        assert_checker_match(expect_exc_message, str(exc))


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
