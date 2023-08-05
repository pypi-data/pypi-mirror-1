#! /usr/bin/env python

"""
setup.py

Copyright (C) 2006 David Boddie

This file is part of PyPI Browser, a GUI browser for the Python Package Index.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

from distutils.core import setup
from PyPIBrowser.constants import __version__


setup(
    name="PyPI-Browser",
    version=__version__,
    author="David Boddie",
    author_email="david@boddie.org.uk",
    url="http://www.boddie.org.uk/david/Projects/Python/PyPI-Browser/",
    description="A GUI browser for the Python Package Index",
    long_description="PyPI Browser is a PyQt4-based GUI browser for the "
                     "Python Package Index that retrieves package information "
                     "an XML-RPC interface.",
    download_url="http://cheeseshop.python.org/packages/source/P/PyPI-Browser/PyPI-Browser-%s.zip" % __version__,
    scripts=["pypibrowser.py"],
    packages=["PyPIBrowser"],
    package_data={"PyPIBrowser": ["Documents/*.html"]}
    )
