#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Scripy Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Absolute path of files."""


class Bin(object):
    """Avoid possible trojans into executables from a modified *PATH*."""
    # /bin
    chown = '/bin/chown'
    cp = '/bin/cp'
    grep = '/bin/grep'
    ls = '/bin/ls'
    readlink = '/bin/readlink'
    sed = '/bin/sed'

    # /sbin
    modprobe = '/sbin/modprobe'

    # /usr/bin
    apt_get = '/usr/bin/apt-get'
    diff = '/usr/bin/diff'
    find = '/usr/bin/find'
    stat = '/usr/bin/stat'
    sudo = '/usr/bin/sudo'
