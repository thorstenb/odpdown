#!/usr/bin/env python

import os.path
from setuptools import setup
import setuptools.command.install
import subprocess

def install_vim_plugin(install_scripts):
    print('installing vim plugin')
    subprocess.call(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins', 'vim', 'setup.py'), install_scripts])

def handle_plugins(command):
    command.user_options.append( ('install-vim', None, 'install vim plugin too') )
    wrapped_run = command.run
    wrapped_initopts = command.initialize_options
    def initialize_options_with_plugins(self):
        self.install_vim = None
        wrapped_initopts(self)
    def run_with_plugins(self):
        if(self.install_vim and not self.user):
            raise Exception("Sorry, the vim plugin is currently only support for --user installs. Patches welcome.")
        wrapped_run(self)
        if(self.install_vim):
            install_vim_plugin(self.install_scripts)
    command.run = run_with_plugins
    command.initialize_options = initialize_options_with_plugins
    return command

@handle_plugins
class install(setuptools.command.install.install):
    pass

setup(name='odpdown',
      description='Generate OpenDocument Presentation (odp) files'
      ' from markdown',
      version='0.4.1',
      author='Thorsten Behrens',
      author_email='tbehrens@acm.org',
      url='https://github.com/thorstenb/odpdown.git',
      long_description=open('README.md').read(),
      python_requires = '>=3.9,<4',
      py_modules=['odpdown'],
      scripts=['odpdown'],
      license='BSD License',
      install_requires=[
          'beautifulsoup4 >= 4.8.2',
          'mistune>=0.7.1, <2.0.0',
          'odfdo>=3.7.7',
          'pygments>=1.6',
          'pillow>=2.0',
          'lxml>=3.4.4, <5.0.0',
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
      ],
      cmdclass={
          'install' : install,
      }
    )
