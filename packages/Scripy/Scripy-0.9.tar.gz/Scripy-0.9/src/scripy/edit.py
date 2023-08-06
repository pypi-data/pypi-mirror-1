#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
Edit - tools to edit text files.
"""

__all__ = ['Edit']

import filecmp
import fnmatch
import os
import shutil
import tempfile

from . import (path, shell, system)

_log = shell.logger(__name__)


class Edit(object):
    """Edit an existing file.

    Use shell commands running through *sudo* so it's possible to edit
    files owned by whatever user.

    ...

    Parameters
    ----------
    filename : str
        The file name to edit.
    do_backup : boolean, optional
        If *True*, do a backup of `filename`.
        Default is *True*.

    Attributes
    ----------
    do_backup
    char : str, optional
        The character used for comments.
        Default is *#*.
    file_path : str
        The canonical path of the specified `filename`.
    dirname : str
        The directory component of `file_path`.
    basename : str
        The final component of `file_path`.
    backup_path : str, optional
        The path of the backup for the `filename`.
    file_user : str
        The user name of owner for `file_path`.
    file_group : str
        The group name of owner for `file_path`.
    user_name : str
        The user name that is running the script.

    Raises
    ------
    PathError
        If the path of `file_path` does not exists.
    FileError
        If the file given on `file_path` does not exists.

    """

    def __init__(self, filename, char='#', do_backup=True):
        # Simulate `os.path.realpath(filename)` but using *sudo*.
        self.file_path = shell._run("{sudo} {readlink} -f {file}".format(
            sudo=path.sudo, readlink=path.readlink, file=filename))[1]

        # Check if the directory exists.
        if not self.file_path:
            try:
                raise PathError(filename)
            except PathError as err:
                _log.error(err.message)
                raise PathError(filename)

        self.dirname = os.path.dirname(self.file_path)
        self.basename = os.path.basename(self.file_path)
        self.backup_path = None
        self.do_backup = do_backup

        # Check if the file exists.
        if not shell._run("{sudo} {find} {dir} -type f -name {file}".format(
            sudo=path.sudo, find=path.find, dir=self.dirname,
            file=self.basename)
        )[1]:
            try:
                raise FileError(self.file_path)
            except FileError as err:
                _log.error(err.message)
                raise FileError(self.file_path)

        # Get both user and group of the file.
        stat_cmd = "{sudo} {stat} {file}".format(
            sudo=path.sudo, stat=path.stat, file=self.file_path)
        self.file_user = shell._run("{0} -c %U".format(stat_cmd))[1]  # User.
        self.file_group = shell._run("{0} -c %G".format(stat_cmd))[1]  # Group.

        # Get the user name that is running the script.
        self.user_name = shell._run("{id} -un".format(id=path.id))[1]

        self.char = char

    def _backup(self):
        """Create a backup of `filename`.

        The schema used to the new names is: *`filename`+`number`~*

            filename : The original file name.
            + : Character used to separate the file name from rest.
            number : Each time that it is made a backup then it is added
                a new number, beginning by '1'.
            ~ : Last character to indicate that it is a backup, as it's
                used in Unix/Linux systems.

        """
        # Check if the file is empty to skip the backup.
        if shell._run("{sudo} {find} {dir} -type f -name {file} -empty".format(
            sudo=path.sudo, find=path.find, dir=self.dirname,
            file=self.basename)
        )[1]:
            return

        # Simulate ``os.listdir(self.dirname)`` but using *sudo*.
        listdir = shell._run("{sudo} {ls} {dir}".format(
            sudo=path.sudo, ls=path.ls, dir=self.dirname)
        )[1].splitlines()

        # Get all backup files, if any.
        all_backup = fnmatch.filter(listdir, "{file}+[0-9]*~".format(
            file=self.basename))

        if all_backup:
            # Get a list of numbers to get the largest one.
            num_backup = [ int(x.split('+')[-1].rstrip('~')) for \
                          x in all_backup ]
            num_backup = "{0}".format(str(max(num_backup) + 1))
        else:
            num_backup = '1'

        # Get the path of the backup.
        backup_base = "{file}+{number}~".format(
            file=self.basename, number=num_backup)
        self.backup_path = os.path.join(self.dirname, backup_base)

        shell._run("{cp} -p {source} {backup}".format(
            cp=path.cp, source=self.file_path, backup=self.backup_path))
        self._setback_chown(self.backup_path)

    def _is_same(self, file1, file2):
        """Check if `file1` and `file2` are the same one.

        ...

        Returns
        -------
        boolean
            *True* if the files seem equal, *False* otherwise.

        """
        if filecmp.cmp(file1, file2):
            return True
        else:
            return False  # store the difference.

    def _setup_tmp(self):
        """Create a temporary file.

        If the user of the file is different then change the file owner
        so it's possible to copy it from python run by whatever user.

        """
        if self.user_name != self.file_user:
            shell._run("{sudo} {chown} {user} {file}".format(
                sudo=path.sudo, chown=path.chown, user=self.user_name,
                file=self.file_path)
            )
            self.is_different_owner = True
        else:
            self.is_different_owner = False

        # Create the temporary file.
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w')

    def _setback_chown(self, filename):
        """Set to the original owner of the file."""
        if self.is_different_owner:
            shell._run("{sudo} {chown} {user}:{group} {file}".format(
                sudo=path.sudo, chown=path.chown, user=self.file_user,
                group=self.file_group, file=filename)
            )

    def _setdown_tmp(self):
        """Remove the temporary file.

        Also set to the original owner of the file.

        """
        self._setback_chown(self.file_path)

        # Close the temporary file.
        self.tmp_file.close()

    def _setwrite_tmp(self):
        """Write the temporary data to disk."""
        self.tmp_file.flush()
        os.fsync(self.tmp_file)

    def append(self, text, overwrite=False):
        """Write the string on `text` to file given on `filename`.

        Use a temporary file to copy the text and then that file is
        copied to the main file, so avoid to have escape the text.

        ...

        Parameters
        ----------
        text : str
            The text string to write into the file.
        overwrite : boolean, optional
            If *True*, truncate `filename` to zero length.
            Default is *False*.

        Returns
        -------
        Code.OK : int
            Exit status code indicating that it was correctly run.

        """
        self._setup_tmp()

        if self.do_backup:
            self._backup()

        if not overwrite:
            shutil.copyfile(self.file_path, self.tmp_file.name)
            # Set the position of temporary file at the end.
            self.tmp_file.seek(0, os.SEEK_END)
        # Append the text.
        self.tmp_file.write(text + '\n')
        self._setwrite_tmp()

        shutil.copyfile(self.tmp_file.name, self.file_path)

        self._setdown_tmp()
        return shell.Code.OK

    def comment(self, search):
        """Comment all lines in `filename` matching `search`.

        Prepend the comment character at the beginning of each line
        matched.

        ...

        Parameters
        ----------
        search : str or list of str
            The pattern to search.

        Returns
        -------
        Code.OK : int
            Exit status code indicating that it was correctly run.

        See Also
        --------
        comment_out

        """
        # Normalize to list.
        if not isinstance(search, list) and not isinstance(search, tuple):
            search = [search]

        expr = ''
        for regex in search:
            expr += " -e '/{regex}/ s/^/{character}/'".format(
                regex=regex, character=self.char)

        self.sed(expr)
        return shell.Code.OK

    def comment_out(self, search, lstrip=False):
        """Comment out all lines in `filename` matching `search`.

        Remove the comment character of the beginning of each line
        matched.

        ...

        Parameters
        ----------
        search : str or list of str
            The pattern to search.
        lstrip : boolean, optional
            If *True*, strip the blank characters at the beginning.
            Default is *False*.

        Returns
        -------
        Code.OK : int
            Exit status code indicating that it was correctly run.

        See Also
        --------
        comment

        """
        # Normalize to list.
        if not isinstance(search, list) and not isinstance(search, tuple):
            search = [search]

        expr_search = ''
        if lstrip:
            expr_search += "[[:space:]]*"
        expr_search += "{character}[[:space:]]*".format(character=self.char)

        expr = ''
        for regex in search:
            expr += " -e '/^[[:space:]]*{char}.*{regex}/ s/{search}//'".format(
                char=self.char, regex=regex, search=expr_search)

        self.sed(expr)
        return shell.Code.OK

    def sed(self, args):
        """Wrapper to *sed* command.

        If there were any change at editing the file then does a backup
        of `filename`.

        ...

        Parameters
        ----------
        args : str
            The arguments passed to *sed*.

        Returns
        -------
        Code.OK : int
            Exit status code indicating that it was correctly run.

        """
        self._setup_tmp()

        shutil.copyfile(self.file_path, self.tmp_file.name)
        sed_cmd = shell._run("{sed} -i {arguments} {file}".format(
            sed=path.sed, arguments=args, file=self.tmp_file.name))[1]
        self._setwrite_tmp()

        # It is possible that there would not changes so the backup is deleted.
        if self.do_backup and \
           not self._is_same(self.file_path, self.tmp_file.name):
            self._backup()
            shutil.copyfile(self.tmp_file.name, self.file_path)

        self._setdown_tmp()
        return shell.Code.OK


# Exceptions
# ==========

class FileError(Exception):

    def __init__(self, filename):
        self.filename = filename
        self.strerror = "doesn't exist or isn't a file"
        self.message = "{0}: {1}".format(self.filename, self.strerror)

    def __str__(self):
        return self.message


class PathError(Exception):

    def __init__(self, dirname):
        self.dirname = os.path.dirname(dirname)
        self.strerror = "directory does not exist"
        self.message = "{0}: {1}".format(self.dirname, self.strerror)

    def __str__(self):
        return self.message
