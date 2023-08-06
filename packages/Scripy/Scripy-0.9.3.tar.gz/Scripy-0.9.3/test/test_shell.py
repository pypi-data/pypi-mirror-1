#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Scripy Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Test suite for command tools."""

from nose import tools

import scripy
from scripy import (_path, shell)


class Path(object):
    """A new class with absolut path for commands."""
    ps = '/bin/ps'


class TestRun(object):
    CMD1 = "{ls} -l".format(ls=_path.Bin.ls)
    CMD2 = "{ls}".format(ls=_path.Bin.ls)
    NON_CMD = 'non -lF '

    run = scripy.Run(cmd_expansion=True, debug=True)
    run_background = scripy.Run(background=True, cmd_expansion=True, debug=True)
    run_no_expand = scripy.Run(cmd_expansion=False, debug=True)
    run_new_path = scripy.Run(bin=Path, cmd_expansion=True, debug=True)

    @tools.raises(EnvironmentError)
    def test_raise_cmd_error(self):
        self.run("{0}".format(self.NON_CMD))

    @tools.raises(EnvironmentError)
    def test_raise_error__no_expand(self):
        self.run_no_expand("!ls -l")

    def test_new_path(self):
        assert self.run_new_path("!ps").returncode == scripy.ReturnCode.OK

    def test_pipe(self):
        assert self.run("{0}|{1}".format(self.CMD1, self.CMD2)).returncode == \
            scripy.ReturnCode.OK

    @tools.raises(shell.PipeError)
    def test_raise_pipe_error(self):
        self.run("{0} |  ".format(self.CMD1))

    def test_expansion_cmd(self):
        assert self.run("!ls").returncode == scripy.ReturnCode.OK

    def test_expansion_cmd2(self):
        assert self.run("!sudo !ls /dev/null").returncode == scripy.ReturnCode.OK

    @tools.raises(shell.ExpansionError)
    def test_expansion_separated(self):
        self.run("! ls")

    def test_command_path_expansion(self):
        assert self.run_background("!{0}".format(self.NON_CMD)) == \
            scripy.ReturnCode.ERROR
