#!/usr/bin/env python
# This is the module's setup script.  To install this module, run:
#
#   python setup.py install
#
# $Id: setup.py 5500 2008-05-29 21:10:07Z lowell $
""" Concurrent logging handler (drop-in replacement for RotatingFileHandler)
Overview
========
This module provides an additional log handler for Python's standard logging
package (PEP 282). This handler will write a log entries to a set of files,
which switches from one file to the next when the current file reaches a certain
size.  Multiple processes can write to the log file concurrently.

Details
=======
The ``ConcurrentRotatingFileHandler`` class is a drop-in replacement for
Python's standard log handler ``RotatingFileHandler``. This module uses file
locking so that multiple processes can concurrently log to a single file without
dropping or clobbering log records. This module provides a file rotation scheme
like ``RotatingFileHanler``, except that extra care is taken to ensure that logs
can be safely rotated before the rotation process is started. (This module works
around the file rename issue with ``RotatingFileHandler`` on Windows, where a
rotation failure means that all subsequent logs are lost).

This module's attempts to preserve log records at all cost. This means that log
files will grow larger than the specified maximum (rotation) size. So if disk
space is tight, you may want to stick with ``RotatingFileHandler``, which will
strictly adhere to the maximum file size.


Installation
============
Use the following command to install this package::

    easy_install ConcurrentLogHandler

If you are installing from source, you can use::

    python setup.py install


Examples
========

Simple Example
--------------
Here is a example demonstrating how to use this module directly (from within
Python code)::

    from logging import getLogger, INFO
    from cloghandler import ConcurrentRotatingFileHandler
    import os
    
    log = getLogger()
    # Use an absolute path to prevent file rotation trouble.
    logfile = os.path.abspath("mylogfile.log")
    # Rotate log after reaching 512K, keep 5 old copies.
    rotateHandler = ConcurrentRotatingFileHandler(logfile, "a", 512*1024, 5)
    log.addHandler(rotateHandler)
    log.setLevel(INFO)
    
    log.info("Here is a very exciting log message, just for you")

Config file example
-------------------
This example shows you how to use this log handler with the logging config file
parser. This allows you to keep your logging configuration code seperate from
your application code.

Example config file: ``logging.ini``::

    [loggers]
    keys=root
    
    [handlers]
    keys=hand01
    
    [formatters]
    keys=form01
    
    [logger_root]
    level=NOTSET
    handlers=hand01
    
    [handler_hand01]
    class=handlers.ConcurrentRotatingFileHandler
    level=NOTSET
    formatter=form01
    args=("rotating.log", "a", 512*1024, 5)
    
    [formatter_form01]
    format=%(asctime)s %(levelname)s %(message)s

Example Python code: ``app.py``::

    import logging, logging.config
    import cloghandler
    
    logging.config.fileConfig("logging.ini")
    log = logging.getLogger()
    log.info("Here is a very exciting log message, just for you")


Changelog
=========

- 0.8.0:  Minor feature release
    * Add better support for using ``logging.config.fileConfig()``. This class
      is now avaiable using ``class=handlers.ConcurrentRotatingFileHandler``.
    * Minor changes in how the ``filename`` parmerer is handled when given a
      relative path.

- 0.7.4:  Minor bug fix
    * Fixed a typo in the package description (incorrect class name)
    * Added a change log; which you are reading now.
    * Fixed the ``close()`` method to no longer assume that stream is still
      open.

To-do
=====
* This module has not yet be tested in a multi-threaded environment. I see no
  reason why this should be an issue, but no stress-testing has been done in a
  threaded situation. If this is important to you, you could always add
  threading support to the ``stresstest.py`` script and send me the patch.

"""




from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup


VERSION = "0.8.0"
classifiers = """\
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Topic :: System :: Logging
Operating System :: POSIX
Operating System :: Microsoft :: Windows
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: Apache Software License
"""
doc = __doc__.splitlines()


setup(name='ConcurrentLogHandler',
      version=VERSION,
      author="Lowell Alleman",
      author_email="lowell87@gmail.com",
      py_modules=[
        "cloghandler",
        "portalocker",
        ],
      package_dir={ '' : 'src', },
      data_files=[
        ('tests', ["stresstest.py"]),
        ('docs', [
            'README',
            'LICENSE',
            ]),
      ],
      url="http://pypi.python.org/pypi/ConcurrentLogHandler",
      license = "http://www.apache.org/licenses/LICENSE-2.0",
      description=doc.pop(0),
      long_description="\n".join(doc),
      platforms = [ "nt", "posix" ],
      classifiers=classifiers.splitlines(),
      zip_safe=True,
      #test_suite=unittest.TestSuite,
)



