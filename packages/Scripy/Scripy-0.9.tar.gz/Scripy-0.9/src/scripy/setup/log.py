#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
setup - setup the logging.
teardown - tear down the logging.
"""

__all__ = ['setup', 'teardown']

import logging
#import traceback


def setup(filename='/tmp/scripy.log'):
    """Configure the logging.

    ...

    Parameters
    ----------
    filename : str
        The file name where logs are going to be written.

    See Also
    --------
    teardown

    Notes
    -----
    Use the date and time international format:
        http://www.w3.org/TR/NOTE-datetime

    """
    # File logger in YAML format.
    # ----------
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            "---\n"
            "Date-Time: %(asctime)s\n"
            "Host: %(host)s\n"
            "Name: %(name)s\n"
            "%(levelname)s:\n"
            "%(message)s"),
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        filename=filename,
        filemode='w')

    # Console logger.
    # ----------
    # Define a handler which writes INFO messages or higher to the 'sys.stderr'.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # Set a format which is simpler for console use.
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    # Tell the handler to use this format.
    console.setFormatter(formatter)
    # Add the handler to the root logger.
    logging.getLogger('').addHandler(console)

    # Don't collect
    # ----------
    #logging.logMultiprocessing = 0
    logging.logProcesses = 0
    logging.logThreads = 0


def teardown():
    """Flush and close all handlers of logging.

    ...

    See Also
    --------
    setup

    """
    logging.shutdown()


def caller(up=1):
    """Get information about the caller function.

    ...

    Parameters
    ----------
    up : int, optional
        Allow retrieval of a caller further back up into the call stack.
        Default is *1*.

    Returns
    -------
    frame : tuple of str
        File name, line number, function name and source text of the
        caller's caller.

    Notes
    -----
    The source text may be *None* and function name may be *?* in the
    returned result. In Python 2.3+ the file name may be an absolute
    path.

    """
    try:  # Just get a few frames.
        frame = traceback.extract_stack(limit=up+2)
        if frame:
            return frame[0]
    except:
        if __debug__:
            traceback.print_exc()
        pass
    # Running with Psyco?
    return ('', 0, '', None)

# http://lackingrhoticity.blogspot.com/2009/09/logging-with-stack-traces.html
# print traceback.print_exc()
# print inspect.stack()[up][0].f_globals['__name__']
