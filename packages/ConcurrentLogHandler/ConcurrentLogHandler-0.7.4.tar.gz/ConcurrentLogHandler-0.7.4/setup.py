#!/usr/bin/env python
# This is the module's setup script.  To install this module, run:
#
#   python setup.py install
#
# $Id: setup.py 5490 2008-05-22 19:03:46Z lowell $
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


Simple example
==============
Here is a example demonstrating how to use this module::

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

"""




from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

VERSION = "0.7.4"
classifiers = """\
Development Status :: 4 - Beta
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
            'CHANGELOG'
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



