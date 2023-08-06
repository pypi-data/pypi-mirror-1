#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Test suite for edition tools."""

import os
import tempfile

from nose import tools

from scripy import (edit, shell)


class TestAccess(object):
    NON_EXIST_DIR = '/tmp2/non_exist'
    NON_EXIST_FILE = '/tmp/non_exist'

    @tools.raises(edit.PathError)
    def test_raise_dir_error(self):
        edit.Edit(self.NON_EXIST_DIR, do_backup=False)

    @tools.raises(edit.FileError)
    def test_raise_file_error(self):
        edit.Edit(self.NON_EXIST_FILE, do_backup=False)


class TestEdit(object):

    @classmethod
    def setup_class(self):
        """Create a temporary file to edit it."""
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w')
        self.edit = edit.Edit(self.tmp_file.name, do_backup=True)

    @classmethod
    def teardown_class(self):
        """Remove the files."""
        file_name = self.tmp_file.name
        self.tmp_file.close()

        files = shell.expand(file_name + '*')
        for path in files.split():
            os.remove(path)

    def check_append(self, text):
        assert self.edit.append(text, overwrite=False) == shell.ReturnCode.OK

    def test_append(self):
        txt = [
            "first",
            "what's happening\nhere?",
            'come on "baby"!',
            "today is \"yesterday\" but not tomorrow.",
        ]
        for i in txt:
            yield self.check_append, i

    def test_comment(self):
        assert self.edit.comment('yesterday') == shell.ReturnCode.OK

    def test_commentout(self):
        assert self.edit.comment_out('yesterday') == shell.ReturnCode.OK
