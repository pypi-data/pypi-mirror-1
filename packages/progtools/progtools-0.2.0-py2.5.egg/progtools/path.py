#!/usr/bin/env python
#
#   path.py
#   progtools
#
#   Copyright (C) 2008 Ross Light
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
Path/file functions

:Variables:
    STREAM_CODE : str
        The special file name that designates standard input or output
"""

import os
import sys

__author__ = 'Ross Light'
__date__ = 'December 7, 2008'
__docformat__ = 'reStructuredText'
__license__ = 'MIT'
__all__ = ['STREAM_CODE',
           'expandpath',
           'open_input_file',
           'open_output_file',]

STREAM_CODE = '-'

def expandpath(path):
    """
    Expands a path so that it is usable by the program.
    
    At this time, it just expands the user and normalizes.
    
    :Parameters:
        path : str
            The path to expand
    :Returns: Expanded path
    :ReturnType: str
    """
    return os.path.normpath(os.path.expanduser(path))

def open_input_file(filename=STREAM_CODE, mode='r'):
    """
    Opens a file for input.
    
    :Parameters:
        filename : str
            File name to open.  If '-' is specified, stdin is returned.
        mode : str
            Mode to open the file as.  Default is 'r'.
    :Returns: The opened file
    :ReturnType: file
    """
    if filename == STREAM_CODE:
        return sys.stdin
    else:
        return open(expandpath(filename), mode)
    
def open_output_file(filename=STREAM_CODE, mode='w'):
    """
    Opens a file for output.
    
    :Parameters:
        filename : str
            File name to open.  If '-' is specified, stdout is returned.
        mode : str
            Mode to open the file as.  Default is 'w'.
    :Returns: The opened file
    :ReturnType: file
    """
    if filename == STREAM_CODE:
        return sys.stdout
    else:
        return open(expandpath(filename), mode)
