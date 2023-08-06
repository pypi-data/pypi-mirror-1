#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
Code - exit status codes.
Run - run shell commands.
expand - pattern expansion.
"""

__all__ = ['Code', 'Run', 'expand']

import glob
import logging
import shlex
import subprocess
import sys
import textwrap

from . import path


class _LoggerAdapter(logging.LoggerAdapter):
    """Prepend an indentation to the logging message.

    Subclass `LoggerAdapter` and override `process()`.

    """
    SPACE = '  '  # 2 chars.
    wrapper = textwrap.TextWrapper(initial_indent=SPACE, subsequent_indent=SPACE)

    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra
        return self.wrapper.fill(msg), kwargs


class _LoggerExtra(object):
    """The `extra` context information passed to `LoggerAdapter`."""

    def __getitem__(self, name):
        """Allow this instance to look like a dict."""
        if name == 'host':
            result = Run().__call__("{hostname}".format(
                hostname=path.hostname))[1]
        return result

    def __iter__(self):
        """Allow iteration over keys.

        They which will be merged into the `LogRecord` dictionary before
        formatting and output.

        """
        keys = ['host',]
        keys.extend(self.__dict__.keys())
        return iter(keys)  # Better than 'keys.__iter__'


def logger(name):
    """Return an instance of `LoggerAdapter` with the extra fields."""
    return _LoggerAdapter(logging.getLogger(name), _LoggerExtra())

# Internal instance variable of `_LoggerAdapter`.
_log = logger(__name__)


class Code(object):
    """Exit status codes.

    The Unix programs generally use 2 for command line syntax errors
    and 1 for all other kind of errors.

    """
    OK = 0
    ERROR = 1
    CMD_LINE_ERROR = 2

    class Grep(object):
        """Exit codes used by *grep* command."""
        FOUND = 0
        NOT_FOUND = 1
        ERROR = 2


class Run(object):
    """Run a command on the same shell.

    It's possible to pipe the commands, and also pass the shell
    variables.

    ...

    Parameters
    ----------
    verbose : boolean, optional
        If *True*, log all commands called.
        Default is *False*.

    Attributes
    ----------
    verbose

    Notes
    -----
    Don't make the pattern expansion (* ?).

    """
    PIPE = '|'

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __call__(self, command):
        """Run the command.

        Parameters
        ----------
        command : str
            The shell command.

        Returns
        -------
        tuple of int, str
            The exit status code and the output of the command run.

        Raises
        ------
        EnvironmentError
            If the command could not been run.
        PipeError
            If there is not a command after of a pipe.

        """
        process = {}

        if command.rstrip().endswith(self.PIPE):
            try:
                raise PipeError(command)
            except PipeError as err:
                _log.error(err.message)
                raise PipeError(command)

        # Split the different commands.
        l_command = command.split(self.PIPE)

        try:
            # Assign a process to each command.
            for num, cmd in enumerate(l_command):
                env = {}  # Store environment variables.
                num_ = num + 1

                # `shlex` lets manage quotes in shell-like syntaxes.
                cmd_ = shlex.split(cmd)
                # Check if there is some environment variable.
                for i in cmd_[:]:  # Use a copy.
                    if '=' in i:
                        var = i.split('=')
                        env[var[0]] = var[1]
                        # Remove the variable from command.
                        cmd_.remove(i)

                if num_ is 1:
                    process[num_] = subprocess.Popen(
                        cmd_, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env=env)
                else:
                    # Pipe to the anterior command through `stdin`.
                    process[num_] = subprocess.Popen(
                        cmd_, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        stdin=process[num_ - 1].stdout, env=env)

            # `num_` indicates the last process.
            (stdout, stderr) = process[num_].communicate()
        except EnvironmentError as err:
            _log.error("$ {0}: {1}".format(command, err.strerror))
            raise EnvironmentError(err)

        if self.verbose:
            _log.info("$ {0}".format(command))
        # Both `stdout` and `stderr` return '\n' at the end so it's removed.
        if stderr:
            stderr_ = stderr.rstrip()
            _log.error(stderr_)
            raise EnvironmentError(stderr)

        return process[num_].returncode, stdout.rstrip()

    def sudo(self):
        """Run *sudo*.

        If something command needs to use *sudo* since script, then you
        could use this function at the beginning so there is no wait
        until that been requested later.

        """
        self.__call__("{sudo} {cat} /dev/null".format(
            sudo=path.sudo, cat=path.cat))


def expand(file_path):
    """Do the pattern expansion as in the shell.

    ...

    Returns
    -------
    str
        The file given on `file_path` if there is not expansion.

    list of str
        All files from pattern expansion.

    """
    if '*' in file_path or '?' in file_path:
        files = glob.glob(file_path)
        return ' '.join(files)

    return file_path


# Exceptions
# ==========

class PipeError(Exception):

    def __init__(self, command):
        self.command = command
        self.strerror = "no command after of pipe"
        self.message = "$ {0}: {1}".format(self.command, self.strerror)

    def __str__(self):
        return self.message


# This instance variable of `Run` is to be only used on this same package.
_run = Run()
