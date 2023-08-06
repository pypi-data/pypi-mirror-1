#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Absolute path of files.

Avoid possible trojans into executables from a modified PATH.
"""

# /bin
cat = '/bin/cat'
chown = '/bin/chown'
cp = '/bin/cp'
dd = '/bin/dd'
dmesg = '/bin/dmesg'
echo = '/bin/echo'
grep = '/bin/grep'
hostname = '/bin/hostname'
kill = '/bin/kill'
ls = '/bin/ls'
mount = '/bin/mount'
ps = '/bin/ps'
readlink = '/bin/readlink'
rm = '/bin/rm'
sed = '/bin/sed'
umount = '/bin/umount'
uname = '/bin/uname'

# /sbin
cryptsetup = '/sbin/cryptsetup'
losetup = '/sbin/losetup'
lvcreate = '/sbin/lvcreate'
modprobe = '/sbin/modprobe'
parted = '/sbin/parted'
partprobe = '/sbin/partprobe'
pvcreate = '/sbin/pvcreate'
start_stop_daemon = '/sbin/start-stop-daemon'
tune2fs = '/sbin/tune2fs'
vgcreate = '/sbin/vgcreate'
vgdisplay = '/sbin/vgdisplay'
mkfs = {
    'ext4': '/sbin/mkfs.ext4',
    'nilfs2': '/sbin/mkfs.nilfs2',
    'vfat': '/sbin/mkfs.vfat',
}

# /usr/bin
apt_get = '/usr/bin/apt-get'
dcfldd = '/usr/bin/dcfldd'
diff = '/usr/bin/diff'
find = '/usr/bin/find'
head = '/usr/bin/head'
id = '/usr/bin/id'
stat = '/usr/bin/stat'
sudo = '/usr/bin/sudo'
tail = '/usr/bin/tail'
touch = '/usr/bin/touch'


class Proc(object):
    meminfo = '/proc/meminfo'
    mounts = '/proc/mounts'
