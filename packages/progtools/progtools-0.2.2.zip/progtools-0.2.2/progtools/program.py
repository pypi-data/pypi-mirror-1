#!/usr/bin/env python
#
#   program.py
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
Program execution utilities

:Variables:
    DEFAULT_STATUS_CODES : dict
        Defaults for status codes if the operating system does not provide
        them.
"""

import optparse
import os
import sys

from progtools import errors

__author__ = 'Ross Light'
__date__ = 'December 7, 2008'
__docformat__ = 'reStructuredText'
__license__ = 'MIT'
__all__ = ['DEFAULT_STATUS_CODES',
           'StatusMixIn',
           'OptionParser',
           'get_program_name',
           'status',
           'saferun',
           'catchexits',
           'reportexits',]

DEFAULT_STATUS_CODES = {
    'EX_OK': 0,
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
    'EX_NOTFOUND': 1,
}

class StatusMixIn:
    """Mix-in class for ``OptionParser`` that uses the `status` function."""
    def error(self, msg):
        msg = "%s: error: %s\n" % (self.get_prog_name(), msg)
        self.print_usage(sys.stderr)
        self.exit(status('EX_USAGE'), msg)

class OptionParser(StatusMixIn, optparse.OptionParser):
    """``OptionParser`` subclass that uses the `status` function."""
    pass

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
            return DEFAULT_STATUS_CODES[name]
        except KeyError:
            raise ValueError("Not a valid exit code name: %r" % name)

def saferun(func, args=[], kw={}, usage=None, verbose=False):
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
    * `UsageError`
    
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
        usage : str
            The program's usage string.  If not given, then this function will
            try to find a string set by the `usage` function.
        verbose : bool
            If ``True``, ``IOError``s and ``OSError``s will print a
            pretty error message.
    :Returns: The return value of the function
    :ReturnType: int
    """
    # Get usage
    if usage is None:
        usage = getattr(func, 'progtools_usage', None)
    # Run the function
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
    except errors.UsageError, e:
        if verbose:
            program_name = get_program_name()
            if str(e):
                print >> sys.stderr, "%s: usage: %s" % (program_name, e)
            elif usage:
                print >> sys.stderr, "%s: usage: %s" % (program_name, usage)
            else:
                print >> sys.stderr, "%s: usage error" % (program_name)
        return status('EX_USAGE')
    except:
        raise

# Decorators

try:
    # Python 2.5+
    from functools import update_wrapper
except ImportError:
    # Pre-2.5
    def update_wrapper(wrapper, wrapped):
        wrapper.__module__ = wrapped.__module__
        wrapper.__name__ = wrapped.__name__
        wrapper.__doc__ = wrapped.__doc__
        wrapper.__dict__.update(getattr(wrapped, '__dict__', {}))
        return wrapper

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
    update_wrapper(_catchexits, func)
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
    update_wrapper(_reportexits, func)
    return _reportexits

def usage(string):
    """
    Decorate a function with usage.
    
    Designed to be called as such::
    
        >>> # 2.4 decorator syntax
        >>> @usage('spam')
        ... def eggs():
        ...     pass
        ... 
        >>> eggs.progtools_usage
        'spam'
        >>> # Or, for pre-2.4:
        >>> def old_func():
        ...     pass
        ... 
        >>> old_func = usage('Very old')(old_func)
        >>> old_func.progtools_usage
        'Very old'
    
    :Parameters:
        string : str
            The usage string to associate
    :Returns: A function that can be called with a function to wrap
    :ReturnType: function
    :See: saferun
    """
    def _set_usage(func):
        func.progtools_usage = string
        return func
    return _set_usage
