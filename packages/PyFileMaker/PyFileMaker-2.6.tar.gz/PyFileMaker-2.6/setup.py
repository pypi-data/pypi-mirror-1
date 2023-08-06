#!/usr/bin/env python

from setuptools import setup
from PyFileMaker import __version__

setup(name='PyFileMaker',
      version=__version__,
      description='Python Object Wrapper for FileMaker Server XML Interface',
      author='Pieter Claerhout, Klokan Petr Pridal',
      author_email='pieter@yellowduck.be, klokan@klokan.cz',
      license='http://www.opensource.org/licenses/bsd-license.php',
      url='http://code.google.com/p/pyfilemaker/',
      platforms = ["any"],
      packages=['PyFileMaker']
     )
