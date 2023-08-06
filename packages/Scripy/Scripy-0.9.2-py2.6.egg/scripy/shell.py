#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
ReturnCode - exit status codes.
Run - run system commands.
expand - pattern expansion.
"""

__all__ = ['ReturnCode', 'Run', 'expand']

import collections
import glob
import logging
import re
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
            result = Run().__call__("!hostname").stdout
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


class ReturnCode(object):
    """Exit status codes.

    The Unix convention is returning an exit code indicating whether
    there was an error or not.

    ...

    Notes
    -----
    The Unix programs generally use *2* for command line syntax errors
    and *1* for all other kind of errors.

    """
    OK = 0
    ERROR = 1
    CMD_LINE_ERROR = 2

    # Exit codes indicating non-error for these commands.
    cmp = [0, 1]
    diff = [0, 1]
    grep = [0, 1]

    class Grep(object):
        """Meaning of valid codes for the command *grep*."""
        FOUND = 0
        NOT_FOUND = 1


class Run(object):
    """Run a command on the same shell.

    It's possible to pipe the commands, and also pass the shell
    variables.

    ...

    Parameters
    ----------
    background : boolean, optional
        If *True*, the exceptions are not raised else that they are
        logged. Useful for daemons or other background processes.
        Default is *False*.
    bin : class variables as str, optional
        The absolute path of the commands to use by *Scripy*.
        Default is `path.Bin()`.
    cmd_expansion : boolean, optional
        If *True*, expand the absolute path of commands that start with
        `SIGN_EXPANSION`.
        Default is *True*.
    debug : boolean, optional
        If *True*, log all commands called.
        Default is *False*.

    Attributes
    ----------
    PIPE : str
        The sign of a shell pipe.

    SIGN_EXPANSION : str
        The sign to get the absolute path of a command.
    Output : named tuple of int, str
        The exit status code and the output of the command run.
    background
    bin
    cmd_expansion
    debug

    Notes
    -----
    Don't make the pattern expansion (* ?).

    If a command is prepended with *!* then get the absolute path from
    the instance `bin`. Examples:

        Without command expansion::
            from scripy import path
            run("{sudo} {cat} /dev/null".format(
                sudo=path.Bin.sudo, cat=path.Bin.cat))

        VS::
            run("!sudo !cat /dev/null")

    """
    PIPE = '|'
    SIGN_EXPANSION = '!'
    Output = collections.namedtuple('Output', 'returncode, stdout')

    # For the command expansion
    # -------------------------
    _QUOTE1 = "'" + SIGN_EXPANSION
    _QUOTE2 = '"' + SIGN_EXPANSION
    # These tags are to replace the quotes from above.
    _TAG1 = "'__TAG1__"
    _TAG2 = '"__TAG2__'

    def __init__(self, bin=path.Bin(), background=False, cmd_expansion=True,
                 debug=False):
        self.background = background
        self.bin = bin
        self.cmd_expansion = cmd_expansion
        self.debug = debug

    def __call__(self, command):
        """Run the command.

        Parameters
        ----------
        command : str
            The system command.

        Returns
        -------
        Output

        Raises
        ------
        EnvironmentError
            If the command could not been run.
        PipeError
            If there is not a command after of a pipe.

        """
        process = {}

        if command.rstrip().endswith(self.PIPE):
            return self.throw(PipeError, command, 'no command after of pipe')

        # Split the different commands.
        l_command = command.split(self.PIPE)

        if self.debug:
            _log.debug("$ *{0}*".format(command))

        try:
            # Assign a process to each command.
            for num, cmd in enumerate(l_command):
                env = {}  # Store the environment variables.
                cmd_ = cmd  # Work with a copy of command's arguments.
                num_ = num + 1

                # Path expansion for commands.
                if self.cmd_expansion:
                    expand_cmd = []  # Commands to expand its path.

                    # An argument (enclosed in quotes) of any system command
                    # could start with `SIGN_EXPANSION`, so it's replaced for
                    # a tag.
                    if self._QUOTE1 in cmd:  # For simple quotes.
                        cmd_ = cmd.replace(self._QUOTE1, self._TAG1)
                    elif self._QUOTE2 in cmd:  # For double quotes.
                        cmd_ = cmd.replace(self._QUOTE2, self._TAG2)

                    # The arguments are splitted without break the quotes to
                    # get the commands to expand.
                    for arg in shlex.split(cmd_):
                        if arg.startswith(self.SIGN_EXPANSION):
                            expand_cmd.append(arg.lstrip(self.SIGN_EXPANSION))

                    # Once time that know which commands are going to be
                    # replaced, get again the arguments and replace the commands
                    # for its absolute path.
                    cmd_ = cmd
                    for i in expand_cmd:
                        # It's empty because the expansion sign isn't
                        # together to the command.
                        if not i:
                            return self.throw(
                                ExpansionError,
                                cmd,
                                'the expansion sign has to be together to'
                                ' the command'
                                )

                        try:
                            path_cmd = getattr(self.bin, i)
                        # If the command doesn't exist.
                        except AttributeError as err:
                            return self.throw(
                                CommandError,
                                i,  # The command name.
                                'command not found in the class variables',
                                self.bin.__module__
                                )

                        cmd_ = re.sub(
                            r"{sign}{command}".format(
                                sign=self.SIGN_EXPANSION, command=i),
                            "{path_cmd}".format(path_cmd=path_cmd),
                            cmd_
                        )

                # `shlex` lets manage quotes in shell-like syntaxes.
                cmd_split = shlex.split(cmd_)

                # Check if there is some environment variable.
                for i in cmd_split[:]:  # Use a copy.
                    if '=' in i:
                        var = i.split('=')
                        env[var[0]] = var[1]
                        # Remove the variable from arguments.
                        cmd_split.remove(i)

                if num_ is 1:
                    process[num_] = subprocess.Popen(
                        cmd_split, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, env=env)
                else:
                    # Pipe to the anterior command through `stdin`.
                    process[num_] = subprocess.Popen(
                        cmd_split, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, stdin=process[num_ - 1].stdout,
                        env=env)

                if self.debug and self.cmd_expansion:
                    _log.debug("=> *{0}*".format(cmd_))

            # `num_` indicates the last process.
            (stdout, stderr) = process[num_].communicate()
        except EnvironmentError as err:
            _log.exception('"{0}", {1}'.format(cmd_, repr(err)))
            if self.background:
                return self.Output(returncode=ReturnCode.ERROR, stdout=None)
            else:
                raise EnvironmentError('"{0}", {1}'.format(cmd_, str(err)))

        # Both `stdout` and `stderr` return '\n' at the end so it's removed.
        if stderr:
            stderr_ = stderr.rstrip()
            _log.error('"{0}", {1}'.format(cmd_, stderr_))
            if not self.background:
                raise EnvironmentError('"{0}", {1}'.format(cmd_, stderr))

        return self.Output(returncode=process[num_].returncode,
                           stdout=stdout.rstrip())

    def throw(self, exception, *args):
        """Throw an `exception` passing it the arguments from `args`.

        The exception is caught to log it if the command is being run
        in the background.

        ...

        Parameters
        ----------
        exception : class
            The name of the exception to throw.
        args : tuple of str
            The arguments to pass to the exception.

        Returns
        -------
        Output
            The error exit code.

        Raises
        ------
        exception
            If `background` is *False*, raises the same exception with
            that was called.

        """
        try:
            raise exception(*args)
        except exception as err:
            _log.exception(repr(err))
            if self.background:
                return self.Output(returncode=ReturnCode.ERROR, stdout=None)
            else:
                raise exception(str(err))

    def sudo(self):
        """Run *sudo*.

        If anything command needs to use *sudo* from a script, then
        could be used this function at the beginning so there is not
        to wait until that it been requested later.

        """
        self.__call__("!sudo !cat /dev/null")


def check_run_instance(run):
    """Check if `run` is an instance of `Run()`.

    ...

    Parameters
    ----------
    run : class instance
        The class to call system commands.

    Raises
    ------
    RunInstanceError
        If the object given on `run` is not an instance class of `Run()`.

    """
    if not isinstance (run, scripy.shell.Run):
        raise RunInstanceError(run, 'not class instance of `scripy.shell.Run`')


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

class CommandError(Exception):
    pass


class ExpansionError(Exception):
    pass


class PipeError(Exception):
    pass

class RunInstanceError(Exception):
    pass


# This class instance is to be only used on this same package, so each class
# that depends of it will get always the same arguments.
_run = Run(debug=True)
