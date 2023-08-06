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

from setuptools import setup, find_packages
import textwrap

package_name = "burn"
main_module_name = 'burnlib'
main_module = __import__(main_module_name, fromlist=['version'])
version = main_module.version

main_module_doc = main_module.__doc__.decode('utf-8')
short_description, long_description = (
    textwrap.dedent(d).strip()
    for d in main_module_doc.split('\n\n', 1)
    )


setup(
    name=package_name,
    version=version.version,
    packages=find_packages(),
    scripts=[
        "bin/burn",
        "bin/burn-configure",
        ],

    # Setuptools metadata
    zip_safe=False,
    install_requires=[
        "setuptools",
        ],

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
