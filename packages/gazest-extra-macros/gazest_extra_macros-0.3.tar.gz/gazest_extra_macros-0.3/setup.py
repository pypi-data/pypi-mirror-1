#!/usr/bin/python

# Copyright (C) 2007 Yannick Gingras <ygingras@ygingras.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # there is no ez_setup if setup tools is installed with apt, among
    # other things
    pass

try:
    from setuptools import setup, find_packages
except ImportError:
    print "You don't have setuptools installed.  Put ez_setup.py"
    print "in the same directory as setup.py (this script) and try again."
    print "You can get it here:"
    print "  http://peak.telecommunity.com/dist/ez_setup.py"
    sys.exit(1)

from gazest_extra_macros import version

setup(
    name='gazest_extra_macros',
    version=version,
    description="extra wiki macros for gazest",
    author="Yannick Gingras",
    author_email="ygingras@ygingras.net",
    license='GPL v3 or later',
    install_requires=["gazest>=0.3"],
    packages=find_packages(),
    include_package_data=True,
    entry_points="""
    [gazest.wiki_macros]
    math = gazest_extra_macros.math
    echo = gazest_extra_macros.echo
    rst = gazest_extra_macros.rst
    asciidoc = gazest_extra_macros.asciidoc_macros
    markdown = gazest_extra_macros.markdown_macros
    textile = gazest_extra_macros.textile_macros
    social = gazest_extra_macros.social
    """
)
