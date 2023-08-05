#! /usr/bin/env python
#
# Copyright (C) 2001-2006 Python Software Foundation

# Standard distutils setup.py install script for the `mimelib' library, a next
# generation MIME library for Python.  To install into your existing Python
# distribution, run the following at the command line:
#
# % python setup.py install

import sys
from os.path import basename

from distutils.core import setup
from distutils.command.install_lib import install_lib


import email
setup(name='email',
      version=email.__version__,
      description='Standalone email package',
      author='Barry Warsaw',
      author_email='barry@python.org',
      url='http://www.python.org/sigs/email-sig',
      packages=['email'],
      )
