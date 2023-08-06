#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Scripy Authors
# Use of this source code is governed by the ISC License (LICENSE file).

import scripy
import yamlog


def setup_package():
    """Will be executed before tests are run."""
    scripy.Run().sudo()
    yamlog.setup()


def teardown_package():
    """Will be executed after all tests have run."""
    yamlog.teardown()
