#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
load_yaml - load YAML file.
"""

__all__ = ['load_yaml']

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
        f = file(filename, 'r')
        config = yaml.load(f)  #! safe_load ?
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
