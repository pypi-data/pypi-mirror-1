#!/usr/bin/env python
#
#   setup.py
#   progtools
#
#   Copyright (C) 2008-2009 Ross Light
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#

"""
Installation script for progtools

If you want to build a source distribution, then you need to check out the
source from Bazaar_ and install the `setuptools_bzr`_ setuptools plugin.  This
is not necessary if you are building *from* source.

.. _Bazaar: http://bazaar-vcs.org/
.. _setuptools_bzr: https://launchpad.net/setuptoolsbzr
"""

# Bootstrap setuptools
from ez_setup import use_setuptools
use_setuptools()

# Imports
from setuptools import setup, find_packages

# File metadata
__author__ = 'Ross Light'
__date__ = 'December 5, 2008'
__docformat__ = 'reStructuredText'

# Setup
setup(
    name="progtools",
    version="0.2.2",
    packages=find_packages(),
    zip_safe=True,
    # Project metadata
    author="Ross Light",
    author_email="rlight2@gmail.com",
    description="progtools is a simple command-line interface (CLI) library "
                "for Python.",
    license="MIT",
    keywords=["cli", "library", "command", "line", "text",],
    url="http://launchpad.net/progtools",
    download_url="https://launchpad.net/progtools/+download",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
