#!/usr/bin/env python
#
#   progtools.py
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

"""Various utilities for stand-alone command-line programs."""

import optparse
import os
import sys
import traceback
import warnings

__author__ = 'Ross Light'
__date__ = 'February 5, 2006'
__docformat__ = 'reStructuredText'
__license__ = 'MIT'
__all__ = ['expandpath',
           'open_input_file',
           'open_output_file',
           'get_program_name',
           'status',
           'saferun',
           'catchexits',
           'reportexits',
           'StatusMixIn',
           'OptionParser',
           'UsageError',]

### CONSTANTS ###
STREAM_CODE = '-'               # for openInputFile() & openOutputFile()
STATUS_LIST = {'EX_OK': 0,      # for status()
               'EX_USAGE': 2,
               'EX_DATAERR': 1,
               'EX_NOINPUT': 1,
               'EX_NOUSER': 1,
               'EX_NOHOST': 1,
               'EX_UNAVAILABLE': 1,
               'EX_SOFTWARE': 1,
               'EX_OSERR': 1,
               'EX_OSFILE': 1,
               'EX_CANTCREAT': 1,
               'EX_IOERR': 1,
               'EX_TEMPFAIL': 1,
               'EX_PROTOCOL': 1,
               'EX_NOPERM': 1,
               'EX_CONFIG': 1,
               'EX_NOTFOUND': 1,}

### FUNCTIONS ###

def expandPath(*args, **kw):
    warnings.warn("expandPath has changed to expandpath",
                  DeprecationWarning)
    return expandpath(*args, **kw)

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

def openInputFile(*args, **kw):
    warnings.warn("openInputFile has changed to open_input_file",
                  DeprecationWarning)
    return open_input_file(*args, **kw)

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

def openOutputFile(*args, **kw):
    warnings.warn("openOutputFile has changed to open_output_file",
                  DeprecationWarning)
    return open_output_file(*args, **kw)
    
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

def programName(*args, **kw):
    warnings.warn("programName has changed to get_program_name",
                  DeprecationWarning)
    return get_program_name(*args, **kw)

def get_program_name(path=None):
    """
    Gets the program's name, as called by the user.
    
    :Parameters:
        path : str
            The program's path.  Uses ``sys.argv[0]`` by default.
    :Returns: The program's name
    :ReturnType: str
    """
    if path is None:
        path = sys.argv[0]
    return os.path.basename(path)

def status(name):
    """
    Obtains the proper status code for the given name.
    
    If the operating system defines this, then that constant is used.
    Otherwise, a reasonable substitute is used.
    
        >>> import os
        >>> status('EX_OK') == os.EX_OK
        True
        >>> status('EX_USAGE') == os.EX_USAGE
        True
    
    :Parameters:
        name : str
            Name of one of the constants from ``os`` (e.g. ``EX_OK``).
    :Raises ValueError: If the exit code can't be found.
    :Returns: The corresponding status code
    :ReturnType: int
    """
    if not name.startswith('EX_'):
        raise ValueError("Not a valid exit code name: %r" % name)
    os_code = getattr(os, name, None)
    if os_code is not None:
        return os_code
    else:
        try:
            return STATUS_LIST[name]
        except KeyError:
            raise ValueError("Not a valid exit code name: %r" % name)

def saferun(func, args=[], kw={}, verbose=False):
    """
    Runs a function (typically a main function) inside an environment such that
    system exits and keyboard interrupts return, instead of exiting the entire
    program.
    
    `saferun` merely catches certain exceptions and returns codes from the
    status function.  If you catch the exceptions yourself, you can handle it in
    any way you want.
    
    The exceptions caught are:
    * SystemExit
    * KeyboardInterrupt
    * IOError
    * OSError
    
    Any of the exceptions not included above will be raised (for debugging
    purposes).
    
        >>> def spam():
        ...     raise IOError()
        ... 
        >>> saferun(spam) == status('EX_IOERR')
        True
    
    :Parameters:
        func
            Function to call (safely)
        args : list
            Arguments to pass to the function
        kw : dict
            Keyword arguments to pass to the function
    :Keywords:
        verbose : bool
            If ``True``, ``IOError``s and ``OSError``s will print a pretty error
            message.
    :Returns: The return value of the function
    :ReturnType: int
    """
    try:
        return func(*args, **kw)
    except SystemExit, e:
        return e.code
    except KeyboardInterrupt:
        print >> sys.stderr
        return status('EX_OK')
    except IOError, e:
        if verbose:
            print >> sys.stderr, "%s: %s: %s" % (get_program_name(),
                                                 e.filename,
                                                 e.strerror)
        return status('EX_IOERR')
    except OSError, e:
        if verbose:
            print >> sys.stderr, "%s: %s: %s" % (get_program_name(),
                                                 e.filename,
                                                 e.strerror)
        return status('EX_OSERR')
    except UsageError:
        if verbose:
            print >> sys.stderr, "%s: usage error" % (get_program_name())
        return status('EX_USAGE')
    except:
        raise

def catchexits(func):
    """
    Returns a function that automatically saferuns.
    
    Usually used for decorators (Python 2.4 and up).
    
    :Parameters:
        func
            Function to wrap
    :Returns: A wrapped function
    :ReturnType: function
    """
    def _catchexits(*args, **kw):
        return saferun(func, args, kw)
    _catchexits.func_name = func.func_name
    _catchexits.func_doc = func.func_doc
    return _catchexits

def reportexits(func):
    """
    Returns a function that automatically saferuns with verbose on.
    
    Usually used for decorators (2.4 and up).
    
    :Parameters:
        func
            Function to wrap
    :Returns: A wrapped function
    :ReturnType: function
    """
    def _reportexits(*args, **kw):
        return saferun(func, args, kw, verbose=True)
    _reportexits.func_name = func.func_name
    _reportexits.func_doc = func.func_doc
    return _reportexits

### CLASSES ###

class StatusMixIn:
    """Mix-in class for ``OptionParser`` that uses the `status` function."""
    def error(self, msg):
        msg = "%s: error: %s\n" % (self.get_prog_name(), msg)
        self.print_usage(sys.stderr)
        self.exit(status('EX_USAGE'), msg)

class OptionParser(StatusMixIn, optparse.OptionParser):
    """``OptionParser`` subclass that uses the `status` function."""
    pass

class UsageError(Exception):
    """Exception that is raised when a program is used improperly."""
