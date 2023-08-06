#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Scripy Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
load_yaml - load YAML file.
"""

__all__ = ['load_yaml']

import yaml
import yamlog
# In order to use LibYAML based parser and emitter, use the classes CParser
# and CEmitter.
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .. import system

_log = yamlog.logger(__name__)


def load_yaml(filename):
    """Load the YAML configuration file.

    ...

    Parameters
    ----------
    filename : str
        The file name of YAML document.

    Returns
    -------
    config : object
        The corresponding Python object.

    Raises
    ------
    StandardError
        If tle file can not be read.
    YAMLError
        If there is an error with the sintaxis.

    """
    try:
        f = open(filename, 'r')
        config = yaml.load_all(f, Loader=Loader)
    except yaml.YAMLError as err:
        f.close()
        _log.error('can not load YAML file')
        _log.debug(str(err))
        raise yaml.YAMLError(str(err))
    except StandardError as err:
        _log.error('can not load YAML file')
        _log.debug(str(err))
        raise StandardError(str(err))
    else:
        f.close()
        return config
