#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Test suite for command tools."""

from nose import tools

from scripy import (path, shell)


class TestRun(object):

    def test_pipe(self):
        assert shell.Code.OK == shell._run("{ls} | {head} -n1".format(
            ls=path.ls, head=path.head))[0]

    @tools.raises(shell.PipeError)
    def test_raise_pipe_error(self):
        shell._run("{ls} -lF |  ".format(ls=path.ls))

    @tools.raises(EnvironmentError)
    def test_raise_cmd_error(self):
        shell._run('non -lF ')
