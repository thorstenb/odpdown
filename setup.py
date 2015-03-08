#!/usr/bin/env python

from setuptools import setup

setup(name='odpdown',
      description='Generate OpenDocument Presentation (odp) files'
      ' from markdown',
      version='0.4.0',
      author='Thorsten Behrens',
      author_email='tbehrens@acm.org',
      url='https://github.com/thorstenb/odpdown.git',
      long_description=open('README.md').read(),
      py_modules=['odpdown'],
      scripts=['odpdown'],
      license='BSD License',
      install_requires=[
          'mistune>=0.5',
          'lpod-python>=1.1.6',
          'pygments>=1.6',
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
