
The beginning
=============
The shell scripting gets to be non-maintainable code; its sintaxis is very
cryptic and it's very hard to debug. Aside all these negative point increase
at the same time as the size of the program grows.

Here is where Python comes.

Whatever administrator without great knowledge about programming can built basic
scripts fastly after of read the `tutorial`_. Its sintaxis is as pseudo-code so
it's very easy to code. The `basic errors`_ --as syntax errors and exceptions--
help to debug together to the error logging system implemented in `logging`_
module. In addition Python comes with an extensive `standard library`_ of useful
modules which will help to speed up the development of scripts, and if you need
some another module could be searched in the `PyPi`_ repository.

I had forked the *Fabric* project to add the files editing and something other
thing but my goal is very different to that project, aside of that my changes
were not added until that I deleted my forked repository (after many months).


.. _tutorial: http://docs.python.org/tutorial/
.. _basic errors: http://docs.python.org/tutorial/errors.html
.. _logging: http://docs.python.org/library/logging.html
.. _standard library: http://docs.python.org/library/index.html
.. _PyPi: http://pypi.python.org/

Scripy
======
The main tool of this package is the `shell.Run()` class which lets to run
system commands in the same shell. It works well with pipes and pass the shell
variables. It doesn't makes pattern expansion (* ?) as in the shell but could be
used `shell.expand()` instead.

Commands path
-------------
The absolute path of the commands used by *Scripy* are in the *_path* module so
it's avoid some possible trojan. The path is right for Debian/Ubuntu systems
since it's where I can check them.

Without the command expansion, there would be to use::

    import scripy
    from scripy import _path

    run = scripy.Run()
    run("{sudo} {ls} /dev/null".format(sudo=_path.Bin.sudo,
                                       ls=_path.Bin.ls))

But with the command expansion, if any command is prepended with *!* then get
its absolute path::

    run("!sudo !ls /dev/null")

Edit
----
Something that is very important in the shell script is the files editing, and
*Scripy* makes it very easy using the `edit.Edit()` class. It only creates
backups to files that are going to be modified, lets modify files owned by
another users (since that uses *sudo* when the class is instancied), and has
methods for append text, comment or comment out lines that start with a
determined chracter, and a wrapper to *sed* which lets backup the file.

Logging
-------
Yamlog_ manages the error catching code and error reporting.

New scripts
===========
To build scripts based on *Scripy*, it is advised that been created a module
(`_path`) with the new commands to use (that are not in `Scripy._path`), and
another one (`_config`) where to instantiate `scripy.Run()`.

`_path`::

    class Bin(object):
        new_command = '/path/to/new/command'

`_config`::

    import scripy

    from . import _path

    run = scripy.Run(bin=_path.Bin)


.. _Yamlog: http://pypi.python.org/pypi/Yamlog
