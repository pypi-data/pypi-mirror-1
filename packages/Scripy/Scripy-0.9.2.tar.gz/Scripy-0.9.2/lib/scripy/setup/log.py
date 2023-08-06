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
import os
import traceback


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

    Could be used the directory */var/log* but there would be to run it
    as an user with permissions to write there.

    """
    # If */tmp* doesn't exists (not mounted), then will be used the
    # root directory.
    if os.path.isdir(os.path.dirname(filename)):
        filename_ = filename
    else:
        filename_ = '/' + os.path.basename(filename)

    # File logger in YAML format
    # --------------------------
    # Define a handler with rotation of disk log files at 128K.
    logger = logging.handlers.RotatingFileHandler(filename_, maxBytes=131072,
                                                  backupCount=5)
    # Writes DEBUG messages or higher to the 'sys.stderr'.
    logger.setLevel(logging.DEBUG)
    # Set a format in YAML.
    formatter = logging.Formatter(
        "---\n"
        "Date-Time: %(asctime)s\n"
        "Host: %(host)s\n"
        "Name: %(name)s\n"
        "%(levelname)s:\n"
        "%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
        )
    # Tell the handler to use this format.
    logger.setFormatter(formatter)
    # Add the handler to the root logger.
    logging.getLogger('').addHandler(logger)

    # Console logger
    # --------------
    # Write INFO messages or higher to the 'sys.stderr'.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # Set a format which is simpler for console use.
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    # Add the handler to the root logger with the format.
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # Don't collect
    # -------------
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
