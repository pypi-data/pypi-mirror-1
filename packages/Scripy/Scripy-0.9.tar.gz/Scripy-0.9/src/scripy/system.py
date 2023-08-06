#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the 'Scripy' Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
Kernel - tools related to the kernel.
Pkg - basic manage of packages.
"""

__all__ = ['Kernel', 'Pkg']

import os

from . import (path, shell)

_log = shell.logger(__name__)


class Kernel(object):
    """Functions related to the kernel."""

    @staticmethod
    def get_release():
        """Get the kernel release.

        ...

        Returns
        -------
        int
            The kernel version.

        """
        uname_cmd = shell._run("{uname} -r".format(uname=path.uname))
        kernel = uname_cmd[1].split('-')[0].split('.')
        kernel = [int(i) for i in kernel]  # To integer.

        return kernel

    @staticmethod
    def load_modules(*modules):
        """Load modules.

        ...

        Parameters
        ----------
        modules : str, multiple
            The module name without the architecture name.

        Notes
        -----
        To indicate that a module has versions for different
        architectures (AMD or X86), add '-' after of the base name;
        it's chosen the correct architecture.

        Cann't insert all modules together (using *modprobe -a*)
        because it's possible that any module it's compiled in the
        kernel so it would not load the another modules when one faills.

        """
        # Get the architecture.
        mach = shell._run("{uname} -m".format(uname=path.uname))[1]

        if mach != 'x86_64':
            machine = 'i586'
        else:
            machine = mach

        for mod in set(modules):  # Without elements repeated.
            if mod.endswith('-'):
                new_module = mod + machine
            else:
                new_module = mod

            try:
                shell._run("{sudo} {modprobe} {module}".format(
                    sudo=path.sudo, modprobe=path.modprobe, module=new_module))
            except EnvironmentError:
                pass


class Pkg(object):
    """Install packages according to the operating system.

    ...

    Attributes
    ----------
    system : str
        The Linux system name which is got automatically.

    Raises
    ------
    SystemNotSupportedError
        If the system is not supported, by now.

    Notes
    -----
    It's only supported the installation on Debian/Ubuntu systems.

    """
    INSTALL_CMD = {
        'debian': "{apt_get} install".format(apt_get='path.apt_get')
    }

    def __init__(self):
        if os.path.exists('/etc/debian_version'):  # Debian and Ubuntu.
            self.system = 'debian'
        else:
            try:
                raise SystemNotSupportedError()
            except SystemNotSupportedError as err:
                _log.warning(err.message)
                raise SystemNotSupportedError()

    def _call(self, cmd, pkg):
        """Run the command related to a package.

        ...

        Parameters
        ----------
        cmd : str
            Command got of `INSTALL_CMD` variable.
        pkg : str
            Package name.

        """
        shell._run("sudo {command} {package}".format(command=cmd, package=pkg))

    def install(self, pkg):
        """Install a package.

        ...

        Parameters
        ----------
        pkg : str
            Package name.

        """
        self._call(self.INSTALL_CMD[self.system], pkg)


# Exceptions
# ==========

class SystemNotSupportedError(Exception):

    def __init__(self):
        self.strerror = "system not supported to manage packages"
        self.message = "Package: {0}".format(self.strerror)

    def __str__(self):
        return self.message
