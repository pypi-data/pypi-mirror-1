#!/usr/bin/env python

from distutils.core import setup

import autoinstall as package


setup(name=package.__name__,
      version=package.__version__,
      description = package.__doc__.split("\n")[0],
      author='Daniel Krech',
      author_email='eikeon@eikeon.com',
      url='http://eikeon.com/2008/autoinstall/',
      py_modules=['autoinstall'],
     )
