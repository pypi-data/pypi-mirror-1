#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
load_yaml - load YAML file.
"""

__all__ = ['load_yaml']

import sys

import yaml

from .. import (shell, system)

_log = shell.logger(__name__)


def load_yaml(filename):
    """Load the YAML configuration file.

    ...

    Parameters
    ----------
    filename : str
        The file name of YAML document.

    Returns
    -------
    `config` or `Code.ERROR`

    config : object
        The corresponding Python object.
    Code.ERROR : int
        Exit status code indicating that there was a failure,
        intercepted by `StandardError`.

    Raises
    ------
    StandardError
        If tle file can not be read.
    YamlLoadError
        If there is an error with the sintaxis, intercepted by
        `yaml.YAMLError`.

    """
    try:
        f = file(filename, 'r')
        config = yaml.load(f)  #! safe_load ?
    except yaml.YAMLError as err:
        _log.error(err)
        if hasattr(err, 'problem_mark'):
            mark = err.problem_mark
            _log.debug("Line: {line}:{column}".format(
                line=mark.line+1, column=mark.column+1))

        f.close()
        raise YamlLoadError(filename)

    except StandardError as err:
        _log.error(err)
        raise StandardError(err)

    else:
        f.close()
        return config


class YamlLoadError(Exception):

    def __init__(self, filename):
        self.filename = filename
        self.strerror = "can not load YAML file"
        self.message = "{0}: {1}".format(self.filename, self.strerror)

    def __str__(self):
        return self.message
