#!/usr/bin/env python

from setuptools import setup
from odpgenerator import __version__

setup(name='odpgenerator',
      description='Generate OpenDocument Presentation (odp) files'
      ' from markdown',
      version=__version__,
      author='Thorsten Behrens',
      author_email='tbehrens@acm.org',
      url='https://github.com/thorstenb/odpgen.git',
      long_description=open('README.md').read(),
      py_modules=['odpgenerator'],
      scripts=['odpgenerator'],
      license='BSD License',
      install_requires=[
          'mistune>=0.5',
          'lpod-python>=1.1.6',
          'pygments>=2.0',
          'pillow>=2.0',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Graphics :: Presentation',
          'Topic :: Software Development :: Documentation',
          'Topic :: Office/Business'
      ])
