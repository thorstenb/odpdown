#!/usr/bin/env python

from distutils.core import setup

setup(name='odpgenerator',
      version='0.1',
      description='Generate OpenDocument Presentation (odp) files from markdown',
      author='Thorsten Behrens',
      author_email='tbehrens@acm.org',
      url='https://github.com/thorstenb/odpgen.git',
      long_description=open('README.md').read(),
      py_modules=['odpgenerator']
     )
