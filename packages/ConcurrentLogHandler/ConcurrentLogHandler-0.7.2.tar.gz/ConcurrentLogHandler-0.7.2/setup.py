#!/usr/bin/env python
# This is the module's setup script.  To install this module, run:
#
#   python setup.py install
#
""" Concurrent logging handler (replacement for RotatingFileHandler)
The ``ConcurrentRotatingFileHandler`` class is a drop-in replacement for
Python's standard log handler ``RotateFileHandler``. This module uses file
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
"""


from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

VERSION = "0.7.2"
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
            ]),
      ],
      url="http://pypi.python.org/pypi/Concurrent_Log_Handler",
      #url="http://svn.mfps.com/repos/mis/ConcurrentLogHandler",
#      download_url="http://svn.mfps.com/repos/mis/Python/Concurrent-Log-Handler-%s.egg" % VERSION,
      license = "http://www.apache.org/licenses/LICENSE-2.0",
      description=doc.pop(0),
      long_description="\n".join(doc),
      platforms = [ "nt", "posix" ],
      classifiers=classifiers.splitlines(),
      zip_safe=True,
      #test_suite=unittest.TestSuite,
)



