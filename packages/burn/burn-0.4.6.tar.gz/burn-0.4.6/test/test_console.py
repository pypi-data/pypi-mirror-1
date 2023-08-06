# -*- coding: utf-8 -*-

# test/test_console.py
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

""" Unit test module for ‘console’ module.
    """

import __builtin__
import sys
import os
import textwrap
import errno
import tty
import termios

import nose
import nose.tools
import minimock

from burnlib import console


def setup_ask_value_fixtures(testcase):
    """ Set up test fixtures common to ask_value test cases. """
    testcase.mock_tracker = minimock.TraceTracker()

    testcase.test_response = str(object())

    minimock.mock(
        "__builtin__.raw_input",
        returns=testcase.test_response,
        tracker=testcase.mock_tracker)
    minimock.mock(
        "sys.stderr",
        tracker=testcase.mock_tracker)


class ask_value_TestCase(object):
    """ Test cases for ask_value function. """

    def setup(self):
        """ Set up test fixtures. """
        setup_ask_value_fixtures(self)

    def teardown(self):
        """ Test down test fixtures. """
        minimock.restore()

    def test_gets_input_from_console(self):
        """ Should get input from console via ‘raw_input’. """
        test_prompt = "foo"
        expect_mock_output = textwrap.dedent("""\
            Called __builtin__.raw_input(...)
            """) % vars()
        console.ask_value(test_prompt)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_prompt_has_consistent_ending(self):
        """ Should append consistent ending to prompt string. """
        test_prompt = "foo"
        expect_prompt = "%(test_prompt)s? " % vars()
        expect_mock_output = textwrap.dedent("""\
            Called __builtin__.raw_input(%(expect_prompt)r)
            """) % vars()
        console.ask_value(test_prompt)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_returns_expected_response(self):
        """ Should return expected response from standard input. """
        test_prompt = "foo"
        expect_response = self.test_response
        response = console.ask_value(test_prompt)
        nose.tools.assert_equal(expect_response, response)


class ask_value_default_TestCase(object):
    """ Test cases for ask_value function, with default. """

    def setup(self):
        """ Set up test fixtures. """
        setup_ask_value_fixtures(self)

    def teardown(self):
        """ Test down test fixtures. """
        minimock.restore()

    def test_prompt_includes_default(self):
        """ Should prompt including default value. """
        test_prompt = "foo"
        test_default = str(object())
        expect_prompt = "%(test_prompt)s [%(test_default)s]? " % vars()
        expect_mock_output = textwrap.dedent("""\
            Called __builtin__.raw_input(%(expect_prompt)r)
            """) % vars()
        console.ask_value(test_prompt, test_default)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_returns_default_if_empty_response(self):
        """ Should return default value if empty response. """
        test_prompt = "foo"
        test_default = str(object())
        __builtin__.raw_input.mock_returns = ""
        expect_response = test_default
        response = console.ask_value(test_prompt, test_default)
        nose.tools.assert_equal(expect_response, response)


class make_boolean_response_TestCase(object):
    """ Test cases for make_boolean_response function. """

    def test_returns_expected_result(self):
        """ Should return expected result for specified in_text value."""
        scenarios = [
            ('n', {'in_text': "n", 'result': False}),
            ('N', {'in_text': "N", 'result': False}),
            ('no', {'in_text': "no", 'result': False}),
            ('No', {'in_text': "No", 'result': False}),
            ('NO', {'in_text': "NO", 'result': False}),
            ('nO', {'in_text': "nO", 'result': False}),
            ('y', {'in_text': "y", 'result': True}),
            ('Y', {'in_text': "Y", 'result': True}),
            ('ye', {'in_text': "ye", 'result': True}),
            ('Ye', {'in_text': "Ye", 'result': True}),
            ('YE', {'in_text': "YE", 'result': True}),
            ('yes', {'in_text': "yes", 'result': True}),
            ('Yes', {'in_text': "Yes", 'result': True}),
            ('YES', {'in_text': "YES", 'result': True}),
            ]
        for (name, scenario) in scenarios:
            test_case_args = [
                self.check_result_matches,
                scenario['result'], scenario['in_text']]
            yield tuple(test_case_args)

    def check_result_matches(self, expect_result, in_text, default=None):
        args = [in_text]
        result = console.make_boolean_response(*args)
        nose.tools.assert_equal(expect_result, result)

    def test_invalid_input_raises_error(self):
        """ Should raise ValueError for invalid in_text. """
        scenarios = [
            ('empty', {'in_text': ""}),
            ('bogus', {'in_text': "bogus"}),
            ('ni', {'in_text': "ni"}),
            ('nope', {'in_text': "nope"}),
            ('NOPE', {'in_text': "nope"}),
            ('Yarr', {'in_text': "Yarr"}),
            ('yoghurt', {'in_text': "yoghurt"}),
            ('yesterday', {'in_text': "yesterday"}),
            ]
        expect_error = ValueError
        for (name, scenario) in scenarios:
            yield (
                self.check_raises_expected_error,
                expect_error, scenario['in_text'])

    def check_raises_expected_error(self, expect_error, in_text):
        nose.tools.assert_raises(
            expect_error,
            console.make_boolean_response, in_text)

    def test_empty_input_raises_error(self):
        """ Should raise ValueError for empty input. """
        in_text = ""
        expect_error = ValueError
        self.check_raises_expected_error(expect_error, in_text)


class make_yesno_response_TestCase(object):
    """ Test cases for make_yesno_response function. """

    def test_returns_expected_result(self):
        """ Should return expected result for specified in_text value."""
        scenarios = [
            ('false', {'in_value': False, 'result': "no"}),
            ('true', {'in_value': True, 'result': "yes"}),
            ]
        for (name, scenario) in scenarios:
            test_case_args = [
                self.check_result_matches,
                scenario['result'], scenario['in_value']]
            yield tuple(test_case_args)

    def check_result_matches(self, expect_result, in_text, default=None):
        args = [in_text]
        result = console.make_yesno_response(*args)
        nose.tools.assert_equal(expect_result, result)


class get_yesno_response_TestCase(object):
    """ Test cases for get_yesno_response function. """

    def setup(self):
        """ Set up test fixtures. """
        self.mock_tracker = minimock.TraceTracker()

        minimock.mock(
            "console.ask_value",
            returns="yes",
            tracker=self.mock_tracker)
        minimock.mock(
            "sys.stderr",
            tracker=self.mock_tracker)
        minimock.mock(
            "console.make_boolean_response",
            returns=True,
            tracker=self.mock_tracker)

    def teardown(self):
        """ Test down test fixtures. """
        minimock.restore()

    def test_gets_input_from_ask_value(self):
        """ Should get input from console via ‘ask_value’. """
        test_prompt = "foo"
        expect_mock_output = textwrap.dedent("""\
            Called console.ask_value(...)
            ...
            """) % vars()
        console.get_yesno_response(test_prompt)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_prompt_includes_yesno_specifier(self):
        """ Should append yes/no specifier to prompt string. """
        test_prompt = "foo"
        expect_prompt = "%(test_prompt)s (yes/no)" % vars()
        expect_mock_output = textwrap.dedent("""\
            Called console.ask_value(%(expect_prompt)r, None)
            ...
            """) % vars()
        console.get_yesno_response(test_prompt)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_passes_expected_args_to_ask_value(self):
        """ Should pass expected arguments to ‘ask_value’. """
        test_prompt = "foo"
        test_ask_value_prompt_template = "%(test_prompt)s (yes/no)"
        scenarios = [
            ('no default', {
                'in_args': dict(
                    prompt="foo"),
                'call_args': ["foo (yes/no)", None],
                }),
            ('default true', {
                'in_args': dict(
                    prompt="bar", default=True),
                'call_args': ["bar (yes/no)", "yes"],
                }),
            ('no default, spam complaint', {
                'in_args': dict(
                    prompt="baz", complaint="Spam"),
                'call_args': ["baz (yes/no)", None],
                }),
            ('default false, spam complaint', {
                'in_args': dict(
                    prompt="baz", default=False, complaint="Spam"),
                'call_args': ["baz (yes/no)", "no"],
                }),
            ]
        for (name, scenario) in scenarios:
            yield (
                self.check_args_passed_to_function,
                "console.ask_value",
                scenario['in_args'], scenario['call_args'])

    def test_passes_expected_args_to_make_boolean_response(self):
        """ Should pass expected arguments to ‘make_boolean_response’. """
        test_response = "b0gUs"
        scenarios = [
            ('no default', {
                'in_args': dict(
                    prompt="foo"),
                'call_args': [test_response],
                }),
            ('default true', {
                'in_args': dict(
                    prompt="bar", default=True),
                'call_args': [test_response],
                }),
            ('no default, spam complaint', {
                'in_args': dict(
                    prompt="baz", complaint="Spam"),
                'call_args': [test_response],
                }),
            ('default false, spam complaint', {
                'in_args': dict(
                    prompt="baz", default=False, complaint="Spam"),
                'call_args': [test_response],
                }),
            ]
        for (name, scenario) in scenarios:
            yield (
                self.check_args_passed_to_function,
                "console.make_boolean_response",
                scenario['in_args'], scenario['call_args'])

    def check_args_passed_to_function(self, func_name, in_args, call_args):
        console.ask_value.mock_returns = call_args[0]
        console.make_boolean_response.mock_returns = True
        expect_call_args = ", ".join(repr(arg) for arg in call_args)
        expect_mock_output = textwrap.dedent("""\
            ...Called %(func_name)s(%(expect_call_args)s)...
            """) % vars()
        console.get_yesno_response(**in_args)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_returns_expected_result(self):
        """ Should return expected boolean result. """
        scenarios = [
            ('true', {'bool_response': True}),
            ('false', {'bool_response': False}),
            ]
        for (name, scenario) in scenarios:
            expect_result = scenario['bool_response']
            yield (
                self.check_result_matches,
                expect_result, scenario['bool_response'])

    def check_result_matches(self, expect_result, bool_response):
        console.make_boolean_response.mock_returns = bool_response
        test_prompt = "foo"
        result = console.get_yesno_response(test_prompt)
        nose.tools.assert_equal(expect_result, result)

    def test_displays_complaint_when_invalid_input_received(self):
        """ When invalid input, should display specified complaint. """
        expect_error = test_error = ValueError
        console.make_boolean_response.mock_raises = test_error
        test_prompt = "Foo prompt"
        test_complaint = "Bar complaint"
        in_args = dict(
            prompt=test_prompt,
            complaint=test_complaint,
            )
        expect_complaint_output = "%(test_complaint)s\n" % vars()
        expect_mock_output = textwrap.dedent("""\
            ...
            Called sys.stderr.write(%(expect_complaint_output)r)
            """) % vars()
        try:
            console.get_yesno_response(**in_args)
        except expect_error:
            pass
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_displays_nothing_when_valid_input_received(self):
        """ When valid input, should display no complaint. """
        test_prompt = "Foo prompt"
        test_complaint = "Bar complaint"
        in_args = dict(
            prompt=test_prompt,
            complaint=test_complaint,
            )
        unwanted_complaint_output = "%(test_complaint)s\n" % vars()
        unwanted_mock_output = textwrap.dedent("""\
            ...
            Called sys.stderr.write(%(unwanted_complaint_output)r)
            """) % vars()
        console.get_yesno_response(**in_args)
        nose.tools.assert_false(
            self.mock_tracker.check(unwanted_mock_output),
            self.mock_tracker.dump())

    def test_displays_nothing_when_invalid_input_no_complaint(self):
        """ When invalid input but no specified complaint, no display. """
        expect_error = test_error = ValueError
        console.make_boolean_response.mock_raises = test_error
        test_prompt = "Foo prompt"
        in_args = dict(
            prompt=test_prompt,
            )
        unwanted_mock_output = textwrap.dedent("""\
            ...
            Called sys.stderr.write(...)
            """) % vars()
        try:
            console.get_yesno_response(**in_args)
        except expect_error:
            pass
        nose.tools.assert_false(
            self.mock_tracker.check(unwanted_mock_output),
            self.mock_tracker.dump())

    def test_propagates_response_conversion_error(self):
        """ Should propagate ValueError from make_boolean_response. """
        test_prompt = "foo"
        expect_error = test_error = ValueError
        console.make_boolean_response.mock_raises = test_error
        nose.tools.assert_raises(
            expect_error,
            console.get_yesno_response, test_prompt)


class ask_yesno_TestCase(object):
    """ Test cases for ask_yesno function. """

    def setup(self):
        """ Set up test fixtures. """
        self.mock_tracker = minimock.TraceTracker()

        minimock.mock(
            "console.get_yesno_response",
            returns=True,
            tracker=self.mock_tracker)

    def teardown(self):
        """ Test down test fixtures. """
        minimock.restore()

    def test_calls_get_yesno_response_with_expected_args(self):
        """ Should call get_yesno_response with expected arguments. """
        default_complaint = "Please answer [y]es or [n]o."
        scenarios = [
            ('no default', {
                'in_args': dict(
                    prompt="foo"),
                'call_args': ["foo", None, default_complaint],
                }),
            ('default True', {
                'in_args': dict(
                    prompt="foo", default=True),
                'call_args': ["foo", True, default_complaint],
                }),
            ('no default, spam complaint', {
                'in_args': dict(
                    prompt="foo", complaint="Spam"),
                'call_args': ["foo", None, "Spam"],
                }),
            ('default false, spam complaint', {
                'in_args': dict(
                    prompt="foo", default=False, complaint="Spam"),
                'call_args': ["foo", False, "Spam"],
                }),
            ]
        for (name, scenario) in scenarios:
            yield (
                self.check_calls_function_with_expected_arguments,
                "console.get_yesno_response",
                scenario['in_args'], scenario['call_args'])

    def check_calls_function_with_expected_arguments(
        self, func_name, in_args, call_args):
        expect_call_args = ", ".join((repr(arg) for arg in call_args))
        expect_mock_output = (
            "Called %(func_name)s(%(expect_call_args)s)"
            ) % vars()
        console.ask_yesno(**in_args)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def make_mock_get_yesno_response(self, response_sequence):
        """ Make a mock ‘get_yesno_response’ function returning responses. """
        def mock_get_yesno_response(*args):
            response = response_sequence.pop(0)
            if isinstance(response, Exception):
                raise response
            return response
        return mock_get_yesno_response

    def test_calls_get_yesno_response_until_valid_response(self):
        """ Should call get_yesno_response repeatedly until valid.

            Whenever get_yesno_response raises a ValueError, ask_yesno
            should loop and call it again until a valid response is
            received.

            """

        response_sequence = [ValueError("Bad input")] * 5 + [True]
        console.get_yesno_response.mock_returns = None
        console.get_yesno_response.mock_returns_func = (
            self.make_mock_get_yesno_response(response_sequence))
        in_args = ["foo"]
        expect_mock_output = (
            "Called console.get_yesno_response(...)\n"
                * len(response_sequence))
        console.ask_yesno(*in_args)
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_returns_expected_result(self):
        """ Should return expected boolean result. """
        scenarios = [
            ('true', {'bool_response': True}),
            ('false', {'bool_response': False}),
            ]
        for (name, scenario) in scenarios:
            expect_result = scenario['bool_response']
            yield (
                self.check_result_matches,
                expect_result, scenario['bool_response'])

    def check_result_matches(self, expect_result, bool_response):
        console.get_yesno_response.mock_returns = bool_response
        test_prompt = "foo"
        result = console.ask_yesno(test_prompt)
        nose.tools.assert_equal(expect_result, result)


class getch_TestCase(object):
    """ Test cases for getch function. """

    def setup(self):
        """ Set up test fixtures. """
        self.mock_tracker = minimock.TraceTracker()

        minimock.mock(
            "sys.stdin",
            tracker=self.mock_tracker)

        self.mock_stdin_fd = 42
        sys.stdin.fileno.mock_returns = self.mock_stdin_fd

        self.mock_stdin_char = "Θ"
        mock_stdin_stream = [self.mock_stdin_char]
        def mock_stdin_read(size=-1):
            if size < 0:
                size = len(mock_stdin_stream)
            result = "".join(mock_stdin_stream.pop(0) for i in range(size))
            return result
        minimock.mock(
            "sys.stdin.read",
            returns_func=mock_stdin_read,
            tracker=self.mock_tracker)

        self.mock_orig_term_attrs = object()
        self.mock_term_attrs = self.mock_orig_term_attrs
        def mock_tcgetattr(fd):
            if fd == self.mock_stdin_fd:
                return self.mock_term_attrs
            else:
                raise termios.error(errno.EBADF, "Bad file descriptor")
        minimock.mock(
            "termios.tcgetattr",
            returns_func=mock_tcgetattr,
            tracker=self.mock_tracker)
        minimock.mock(
            "termios.tcsetattr",
            tracker=self.mock_tracker)
        minimock.mock(
            "termios.TCSADRAIN")

        def mock_tty_setraw(fd, when=None):
            self.mock_term_attrs = object()
        minimock.mock(
            "tty.setraw",
            returns_func=mock_tty_setraw,
            tracker=self.mock_tracker)

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_sets_stdin_to_unbuffered_mode(self):
        """ Should set stdin terminal to unbuffered (raw) mode. """
        expect_mock_output = textwrap.dedent("""\
            ...
            Called tty.setraw(%(mock_stdin_fd)r)
            ...
            """) % vars(self)
        console.getch()
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_reads_one_char_from_stdin(self):
        """ Should read exactly one character from stdin terminal. """
        expect_mock_output = textwrap.dedent("""\
            ...
            Called sys.stdin.read(1)
            ...
            """) % vars(self)
        console.getch()
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_returns_one_char_from_stdin(self):
        """ Should read exactly one character from stdin terminal. """
        expect_result = self.mock_stdin_char
        result = console.getch()
        nose.tools.assert_equal(expect_result, result)

    def test_propagates_error(self):
        """ Should propagate error from specified function. """
        scenarios = [
            ('tty.setraw error', {
                'error': OSError(), 'func_name': "tty.setraw"}),
            ('sys.stdin.read error', {
                'error': IOError(), 'func_name': "sys.stdin.read"}),
            ]
        for (name, scenario) in scenarios:
            yield (
                self.check_propagates_error,
                scenario['error'], scenario['func_name'])

    def check_propagates_error(self, test_error, error_func_name):
        minimock.mock(
            error_func_name,
            raises=test_error)
        expect_error = test_error
        nose.tools.assert_raises(
            type(expect_error),
            console.getch)

    def test_restores_term_settings(self):
        """ On error or not, should reset stdin terminal settings. """
        scenarios = [
            ('no error', {'error': None}),
            ('tty.setraw error', {
                'error': OSError(), 'func_name': "tty.setraw"}),
            ('sys.stdin.read error', {
                'error': IOError(), 'func_name': "sys.stdin.read"}),
            ]
        for (name, scenario) in scenarios:
            yield (
                self.check_restores_term_settings,
                scenario['error'], scenario.get('func_name'))

    def check_restores_term_settings(self, test_error, error_func_name):
        if test_error:
            minimock.mock(
                error_func_name,
                raises=test_error)
        expect_fd = self.mock_stdin_fd
        expect_when = termios.TCSADRAIN
        expect_attrs = self.mock_orig_term_attrs
        expect_mock_output = textwrap.dedent("""\
            ...
            Called termios.tcsetattr(
                %(expect_fd)r,
                %(expect_when)r,
                %(expect_attrs)r)
            """) % vars()
        try:
            console.getch()
        except type(test_error):
            pass
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))


progressbar_scenarios = {
    '12 wide': {
        'args': [12],
        'width': 12,
        'max_amount': 100,
        },
    '30 wide': {
        'args': [30],
        'width': 30,
        'max_amount': 100,
        'amount': 12,
        },
    }

class ProgressBar_TestCase(object):
    """ Test cases for ProgressBar class. """

    def setup(self):
        """ Set up test fixtures. """
        for (name, scenario) in progressbar_scenarios.items():
            instance = console.ProgressBar(*scenario['args'])
            scenario['instance'] = instance

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_has_specified_width(self):
        """ Should have specified width. """
        attribute_name = 'width'
        for (name, scenario) in progressbar_scenarios.items():
            yield (
                self.check_has_specified_attribute_value,
                name,
                attribute_name, scenario[attribute_name])

    def test_has_specified_max_amount(self):
        """ Should have specified max_amount. """
        attribute_name = 'max_amount'
        for (name, scenario) in progressbar_scenarios.items():
            yield (
                self.check_has_specified_attribute_value,
                name,
                attribute_name, scenario[attribute_name])

    def test_has_zero_amount(self):
        """ Should have initial amount of 0. """
        attribute_name = 'amount'
        for (name, scenario) in progressbar_scenarios.items():
            yield (
                self.check_has_specified_attribute_value,
                name,
                attribute_name, 0)

    def check_has_specified_attribute_value(
        self, scenario_name, attribute_name, expect_value):
        instance = progressbar_scenarios[scenario_name]['instance']
        attribute_value = getattr(instance, attribute_name)
        nose.tools.assert_equal(expect_value, attribute_value)

    def test_set_amount_result_is_as_expected(self):
        """ Should set amount to expected value. """
        test_instance = console.ProgressBar(width=10, max_amount=100)
        scenarios = [
            ('min 0, set 1', {
                'set_amount': 1, 'expect_amount': 1,
                }),
            ('min 0, set 0', {
                'set_amount': 0, 'expect_amount': 0,
                }),
            ('min 0, set -1', {
                'set_amount': -1, 'expect_amount': 0,
                }),
            ('max 100, set 99', {
                'set_amount': 99, 'expect_amount': 99,
                }),
            ('max 100, set 100', {
                'set_amount': 100, 'expect_amount': 100,
                }),
            ('max 100, set 101', {
                'set_amount': 101, 'expect_amount': 100,
                }),
            ]
        for (name, scenario) in scenarios:
            scenario['instance'] = test_instance
            yield (
                self.check_set_amount_result_is_as_expected,
                scenario['expect_amount'],
                scenario['instance'], scenario['set_amount'])

    def check_set_amount_result_is_as_expected(
        self, expect_amount, instance, set_amount):
        instance.amount = set_amount
        nose.tools.assert_equal(expect_amount, instance.amount)

    def test_string_is_as_expected(self):
        """ Should have expected string representation. """
        scenarios = [
            ('width 12, amount 0', {
                'args': {'width': 12},
                'amount': 0,
                'expect_string': "[    0%    ]",
                }),
            ('width 12, max 8, amount 1', {
                'args': {'width': 12, 'max_amount': 8},
                'amount': 1,
                'expect_string': "[=  13%    ]",
                }),
            ('width 32, amount 0', {
                'args': {'width': 32},
                'amount': 0,
                'expect_string': "[              0%              ]",
                }),
            ('width 32, amount 6', {
                'args': {'width': 32},
                'amount': 6,
                'expect_string': "[=             6%              ]",
                }),
            ('width 32, amount 7', {
                'args': {'width': 32},
                'amount': 7,
                'expect_string': "[==            7%              ]",
                }),
            ('width 32, amount 10', {
                'args': {'width': 32},
                'amount': 10,
                'expect_string': "[===          10%              ]",
                }),
            ('width 32, amount 45', {
                'args': {'width': 32},
                'amount': 45,
                'expect_string': "[=============45%              ]",
                }),
            ('width 32, amount 56', {
                'args': {'width': 32},
                'amount': 56,
                'expect_string': "[=============56%              ]",
                }),
            ('width 32, amount 57', {
                'args': {'width': 32},
                'amount': 57,
                'expect_string': "[=============57%=             ]",
                }),
            ('width 32, amount 99', {
                'args': {'width': 32},
                'amount': 99,
                'expect_string': "[=============99%============= ]",
                }),
            ('width 32, amount 100', {
                'args': {'width': 32},
                'amount': 100,
                'expect_string': "[=============100%=============]",
                }),
            ]
        for (name, scenario) in scenarios:
            scenario['instance'] = console.ProgressBar(**scenario['args'])
            yield (
                self.check_string_is_as_expected,
                scenario['expect_string'],
                scenario['instance'], scenario['amount'])

    def check_string_is_as_expected(self, expect_string, instance, amount):
        instance.amount = amount
        string_result = str(instance)
        nose.tools.assert_equal(expect_string, string_result)


class ProgressBar_update_display_TestCase(object):
    """ Test cases for ProgressBar.update_display method. """

    def setup(self):
        """ Set up test fixtures. """
        self.mock_tracker = minimock.TraceTracker()

        self.mock_bar_text = str(object())
        minimock.mock(
            "console.ProgressBar.__str__",
            returns=self.mock_bar_text,
            tracker=self.mock_tracker)

        minimock.mock(
            "sys.stderr",
            tracker=self.mock_tracker)

        self.test_instance = console.ProgressBar(width=12)

    def teardown(self):
        """ Tear down test fixtures. """
        minimock.restore()

    def test_writes_to_stderr(self):
        """ Should write to stderr. """
        instance = self.test_instance
        expect_mock_output = textwrap.dedent("""\
            ...
            Called sys.stderr.write(...)
            ...
            """)
        instance.update_display()
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_writes_string_with_carriage_return(self):
        """ Should write progress bar string with carriage return. """
        instance = self.test_instance
        expect_stderr_output = "%(mock_bar_text)s\r" % vars(self)
        expect_mock_output = textwrap.dedent("""\
            ...
            Called sys.stderr.write(%(expect_stderr_output)r)
            ...
            """ % vars())
        instance.update_display()
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))

    def test_finally_flushes_stderr_buffer(self):
        """ Should finally flush the stderr buffer. """
        instance = self.test_instance
        expect_mock_output = textwrap.dedent("""\
            ...
            Called sys.stderr.flush()
            """)
        instance.update_display()
        nose.tools.assert_true(
            self.mock_tracker.check(expect_mock_output),
            self.mock_tracker.diff(expect_mock_output))


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
