#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

from scripy import shell
from scripy.setup import log


def setup_package():
    """Will be executed before tests are run."""
    shell._run.sudo()
    log.setup()


def teardown_package():
    """Will be executed after all tests have run."""
    log.teardown()
