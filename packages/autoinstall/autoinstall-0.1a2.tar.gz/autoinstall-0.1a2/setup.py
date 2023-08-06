#!/usr/bin/env python

from distutils.core import setup

import autoinstall as package


setup(name=package.__name__,
      version=package.__version__,
      description = package.__doc__.split("\n")[0],
      long_description = package.__doc__,
      author='Daniel Krech',
      author_email='eikeon@eikeon.com',
      url='http://pypi.python.org/pypi/autoinstall/',
      py_modules=['autoinstall'],
     )
