#! /usr/bin/python
# -*- coding: utf-8 -*-

# setup.py
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

""" Python distutils setup for ‘burn’ package.
    """

import distutils.cmd
import distutils.log
from distutils import errors
import os
import os.path
import glob
import subprocess
import re
import textwrap

from setuptools import setup, find_packages
import docutils.core


package_name = "burn"
main_module_name = 'burnlib'
main_module = __import__(main_module_name, fromlist=['version'])
version = main_module.version

main_module_doc = main_module.__doc__.decode('utf-8')
short_description, long_description = (
    textwrap.dedent(d).strip()
    for d in main_module_doc.split('\n\n', 1)
    )


class BuildDocumentationCommand(distutils.cmd.Command):
    """ Build documentation for this distribution. """
    user_options = [
        ("html-src-files=", None,
         "Source files to build to HTML documents."),
        ("manpage-src-files=", None,
         "Source files to build to Unix manpages."),
        ]

    def initialize_options(self):
        """ Initialise command options to defaults. """
        self.document_transforms = {
            'html': {
                'writer_name': 'html',
                'source_suffix_regex': re.compile("\.txt$"),
                'dest_suffix': ".html",
                },
            'manpage': {
                'writer_name': 'manpage',
                'source_suffix_regex': re.compile("\.1\.txt$"),
                'dest_suffix': ".1",
                },
            }

        self.html_src_files = None
        self.manpage_src_files = None

    def finalize_options(self):
        """ Finalise command options before execution. """
        for (transform_name, option_name) in [
            ('html', 'html_src_files'),
            ('manpage', 'manpage_src_files'),
            ]:
            transform = self.document_transforms[transform_name]
            source_paths = []
            source_files_option_value = getattr(self, option_name, None)
            if source_files_option_value is not None:
                source_paths = source_files_option_value.split()
            transform['source_paths'] = source_paths

    def _render_documents(self, transform):
        """ Render documents from reST source. """
        for in_file_path in transform['source_paths']:
            out_file_base = re.sub(
                transform['source_suffix_regex'], "",
                in_file_path)
            out_file_path = out_file_base + transform['dest_suffix']
            distutils.log.info(
                "rendering document %(in_file_path)r -> %(out_file_path)r"
                % vars())
            docutils.core.publish_file(
                source_path=in_file_path,
                destination_path=out_file_path,
                writer_name=transform['writer_name'])

    def run(self):
        """ Execute this command. """
        for transform in self.document_transforms.values():
            self._render_documents(transform)


class BuildReadmeCommand(distutils.cmd.Command):
    """ Build README file for this distribution. """
    user_options = [
        ("input-file=", None,
         "Source HTML file."),
        ("output-file=", None,
         "Destination file to write."),
        ]

    def initialize_options(self):
        """ Initialise command options to defaults. """
        self.input_file = "doc/index.html"
        self.output_file = "README"

    def finalize_options(self):
        """ Finalise command options before execution. """

    def _render_html_to_text(self, in_file_path, out_file_path):
        """ Render HTML document to plain text. """
        render_process_args = [
            "lynx",
            "-dump", "-nolist",
            in_file_path,
            ]
        distutils.log.info(
            "rendering document %(in_file_path)r -> %(out_file_path)r"
            % vars())
        out_file = open(out_file_path, 'w')
        subprocess.Popen(render_process_args, stdout=out_file).wait()

    def run(self):
        """ Execute this command. """
        self._render_html_to_text(self.input_file, self.output_file)


setup(
    name=package_name,
    version=version.version,
    packages=find_packages(),
    scripts=[
        "bin/burn",
        "bin/burn-configure",
        ],
    cmdclass={
        "build_doc": BuildDocumentationCommand,
        "build_readme": BuildReadmeCommand,
        },

    # Setuptools metadata
    zip_safe=False,
    install_requires=[
        "setuptools",
        ],
    tests_require=[
        "nose",
        "MiniMock >=1.2.2",
        ],
    test_suite="nose.collector",

    # PyPI metadata
    author=version.author_name,
    author_email=version.author_email,
    maintainer="Ben Finney",
    maintainer_email="ben+python@benfinney.id.au",
    description=short_description,
    keywords="burn cd dvd media",
    url=main_module._url,
    long_description=long_description,
    license=version.license,
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Console",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Writing",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
        ]
    )


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
