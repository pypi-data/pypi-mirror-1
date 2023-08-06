#!/usr/bin/env python
#
#   __init__.py
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

"""Various utilities for stand-alone command-line programs."""

__author__ = 'Ross Light'
__date__ = 'February 5, 2006'
__docformat__ = 'reStructuredText'
__license__ = 'MIT'
__version__ = '0.2.2'
__all__ = [
    # Sub-modules
    'command',
    'errors',
    'path',
    'program',
    # Globals
    'expandpath',
    'open_input_file',
    'open_output_file',
    'get_program_name',
    'status',
    'saferun',
    'catchexits',
    'reportexits',
    'StatusMixIn',
    'OptionParser',
    'UsageError',
]

# Import sub-modules
from progtools import command
from progtools import errors
from progtools import path
from progtools import program

# Import globals
from progtools.errors import UsageError
from progtools.path import expandpath, open_input_file, open_output_file
from progtools.program import get_program_name, status, \
                              saferun, catchexits, reportexits, \
                              StatusMixIn, OptionParser
