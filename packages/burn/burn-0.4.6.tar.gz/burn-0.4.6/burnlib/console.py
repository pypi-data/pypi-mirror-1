# -*- coding: utf-8 -*-

# burnlib/console.py
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

""" Console interaction functions for ‘burnlib’.

    ask_yesno(prompt, default, complaint)
        Prompts on the console for a yes-or-no response; on bad input,
        displays a complaint and asks again repeatedly.

    getch()
        Get a single character directly from the standard input terminal.

    """

import sys
import tty
import termios


def ask_value(prompt, default=None):
    """ Prompt for an input value from the console.

        The specified `prompt` string is used to prompt for the
        response. If a default is specified, an empty response will
        instead return the default; otherwise, the response as input
        is returned.

        """

    prompt_template = "%(prompt)s? "
    if default is not None:
        prompt_template = "%(prompt)s [%(default)s]? "
    response = raw_input(prompt_template % vars())
    if not response:
        if default is not None:
            response = default
    return response


def make_boolean_response(in_text):
    """ Make a boolean value from the specified response.

        If the `in_text` is a case-insensitive substring match of one
        of the valid words 'no' or 'yes', the result is ``False`` or
        ``True`` respectively.

        If the `in_text` is empty or invalid, a `ValueError` is raised.

        """

    result = None

    response_map = {
        "no": False,
        "yes": True,
        }

    if in_text:
        for word, value in response_map.items():
            if word.find(in_text.lower()) == 0:
                result = value
                break
    if result is None:
        raise ValueError()
    return result


def make_yesno_response(in_value):
    """ Make a "yes"/"no" response string from the specified boolean value.
        """

    result = None

    response_map = {
        False: "no",
        True: "yes",
        }
    result = response_map[in_value]
    return result


def get_yesno_response(prompt, default=None, complaint=None):
    """ Prompt for a yes-or-no response from the console.

        The specified `prompt` string is used to prompt for the
        response. The response is converted to a bool value (with an
        optional default value of `default`) and returned, or
        `ValueError` raised if the conversion fails.

        """

    default_response = None
    if default is not None:
        default_response = make_yesno_response(default)
    response = ask_value("%(prompt)s (yes/no)" % vars(), default_response)
    try:
        result = make_boolean_response(response)
    except ValueError:
        if complaint:
            sys.stderr.write("%(complaint)s\n" % vars())
        raise
    return result


def ask_yesno(prompt, default=None, complaint="Please answer [y]es or [n]o."):
    """ Ask for a response from the console until yes-or-no response. """
    result = None
    while result not in (True, False):
        try:
            result = get_yesno_response(prompt, default, complaint)
        except ValueError:
            pass
    return result


def getch():
    """ Read a single character from the standard input terminal.

        Read and return exactly one character from the stdin terminal
        in raw mode, restoring terminal attributes afterward.

        From recipe <URL:http://code.activestate.com/recipes/134892/>
        by Danny Yoo.

        """
    stdin_fd = sys.stdin.fileno()
    old_term_attributes = termios.tcgetattr(stdin_fd)
    try:
        tty.setraw(stdin_fd)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_term_attributes)
    return char


class ProgressBar(object):
    """ Progress bar for displaying feedback on progress to console. """

    def __init__(self, width, max_amount=100):
        """ Set up a new instance. """
        self.width = width
        self.min_amount = 0
        self.max_amount = max_amount
        self._amount = 0

    def _get_amount(self):
        """ Getter function for ‘amount’ property. """
        return self._amount
    def _set_amount(self, value):
        """ Setter function for ‘amount’ property. """
        self._amount = value
        self._amount = min(self._amount, self.max_amount)
        self._amount = max(self._amount, self.min_amount)
    amount = property(
        fget=_get_amount, fset=_set_amount, fdel=None,
        doc="The current numeric amount of the progress bar.")

    def _amount_ratio(self):
        """ Get the ratio of the amount to the progress span. """
        span = (self.max_amount - self.min_amount)
        amount_ratio = float(self.amount) / span

        return amount_ratio

    def _progress_width(self):
        """ Get the width of the progress area of the bar. """
        progress_width = self.width - len("[]")

        return progress_width

    def _amount_width(self):
        """ Get the width of the current bar amount. """
        progress_width = self._progress_width()
        amount_ratio = self._amount_ratio()
        amount_width = int(progress_width * amount_ratio)

        return amount_width

    def _decorate_bar_with_percentage(self, bar_text):
        """ Decorate the bar text with a percentage of the amount. """
        amount_ratio = self._amount_ratio()
        percent_done = int(round(amount_ratio * 100))

        percent_text = "%(percent_done)d%%" % vars()
        percent_begin_offset = int((len(bar_text) - len(percent_text)) / 2)
        percent_end_offset = percent_begin_offset + len(percent_text)
        bar_text = (
            bar_text[:percent_begin_offset]
            + percent_text
            + bar_text[percent_end_offset:])

        return bar_text

    def __str__(self):
        """ Return the string representation of the progress bar. """
        progress_width = self._progress_width()
        amount_width = self._amount_width()

        amount_ticks = "=" * amount_width
        empty_ticks = " " * (progress_width - amount_width)
        bar_text = "[%(amount_ticks)s%(empty_ticks)s]" % vars()

        bar_text = self._decorate_bar_with_percentage(bar_text)

        return bar_text

    def update_display(self):
        """ Update display of progress bar to stderr. """
        output_text = str(self) + "\r"
        sys.stderr.write(output_text)
        sys.stderr.flush()


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
