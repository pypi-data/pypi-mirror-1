
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

The path of all commands used by *Scripy* are in the *path* module so it's avoid
some possible trojan. The path is right for Debian/Ubuntu systems since it's
where I can check them.

Logging
-------
The logging is configured to write messages in YAML format since it's more easy
to parse, and using the international format for date and time.

To setup the logging, there is that run at beginning of the new script::

  from scripy.setup import log
  log.setup(filename)

where `filename` is */tmp/scripy.log* by default, the file where is going to be
logged.

And for tear down it (after of run all script)::

  log.teardown()

Then, in each module where is going to be used, there is to add at the beginning::

  from scripy import shell
  _log = shell.logger(__name__)

so it pass the module name where it's being run. Now, can be used the methods
--*debug()*, *info()*, *warning()*, *error()* and *critical()*-- to indicate the
importance of a logged message.

Edit
----
Something that is very important in the shell script is the files editing, and
*Scripy* makes it very easy using the `edit.Edit()` class. It only creates
backups to files that are going to be modified, lets modify files owned by
another users (since that uses *sudo* when the class is instancied), and has
methods for append text, comment or comment out lines that start with a
determined chracter, and a wrapper to *sed* which lets backup the file.
