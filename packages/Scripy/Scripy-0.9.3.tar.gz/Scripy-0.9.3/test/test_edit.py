#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Scripy Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Test suite for edition tools."""

import os
import tempfile

from nose import tools

import scripy
from scripy import edit


class TestAccess(object):
    NON_EXIST_DIR = '/tmp2/non_exist'
    NON_EXIST_FILE = '/tmp/non_exist'

    @tools.raises(edit.PathError)
    def test_raise_dir_error(self):
        scripy.Edit(self.NON_EXIST_DIR, do_backup=False)

    @tools.raises(edit.FileError)
    def test_raise_file_error(self):
        scripy.Edit(self.NON_EXIST_FILE, do_backup=False)


class TestEdit(object):
    COMMENT = 'yesterday'
    ROOT_FILE = '/tmp/tmproot'

    @classmethod
    def setup_class(self):
        """Create temporary files to edit them."""
        # A file owned by root.
        run = scripy.Run(cmd_expansion=True, debug=True)
        run("/usr/bin/touch {0}".format(self.ROOT_FILE))
        run("!sudo !chown root {0}".format(self.ROOT_FILE))
        self.run = run
        self.edit_root = scripy.Edit(self.ROOT_FILE, do_backup=False)

        # Another one owned by the user running the script.
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w')
        self.edit_tmp = scripy.Edit(self.tmp_file.name, do_backup=True)

    @classmethod
    def teardown_class(self):
        """Remove the files."""
        file_name = self.tmp_file.name
        self.tmp_file.close()

        files = scripy.expand(file_name + '*')
        for path in files.split():
            os.remove(path)

        # Remove the file owned by root.
        self.run("!sudo /bin/rm {0}".format(self.ROOT_FILE))

    def check_append(self, text):
        assert self.edit_tmp.append(text, overwrite=False) == scripy.ReturnCode.OK

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
        assert self.edit_tmp.comment(self.COMMENT) == scripy.ReturnCode.OK

    def test_commentout(self):
        assert self.edit_tmp.comment_out(self.COMMENT) == scripy.ReturnCode.OK

    def test_root_file(self):
        assert self.edit_root.append(self.COMMENT) == scripy.ReturnCode.OK
