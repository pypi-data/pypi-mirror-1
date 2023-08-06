#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Scripy Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""
Kernel - tools related to the kernel.
Pkg - basic manage of packages.
"""

__all__ = ['Kernel', 'Pkg']

import os
import platform

import yamlog

from ._config import run

_log = yamlog.logger(__name__)


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
        release = platform.release()  # `uname -r`
        kernel = release.split('-')[0].split('.')
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
        mach = platform.machine()  # `uname -m`

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
                run("!sudo !modprobe {module}".format(module=new_module))
            except EnvironmentError:
                pass


class Pkg(object):
    """Install packages according to the operating system.

    ...

    Parameters
    ----------
    background : boolean, optional
        If *True*, the exceptions are not raised else that they are
        logged. Useful for daemons or other background processes.
        Default is *False*.

    Attributes
    ----------
    system : str
        The Linux system name which is got automatically.
    throw : class `yamlog.Throw()`
        Instance to throw exceptions which are logged.
    background

    Raises
    ------
    SupportError
        If the system is not supported, by now.

    Notes
    -----
    It's only supported the installation on Debian/Ubuntu systems.

    """
    INSTALL_CMD = {
        'debian': "!apt_get install"
    }

    def __init__(self, background=False):
        self.throw = yamlog.Throw(_log, background)

        distro = platform.linux_distribution()[0]
        if distro == 'Ubuntu' or distro == 'debian':
            self.system = 'debian'
        else:
            self.throw(
                SupportError,
                'Linux system not supported to manage packages',
                'contact with the author to add support'
                )

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
        run("!sudo {command} {package}".format(command=cmd, package=pkg))

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

class SupportError(Exception):
    pass
