#!/usr/bin/env python

from setuptools import setup
import NagAconda

setup(name=NagAconda.__name__,
      version=NagAconda.__version__,
      description="NagAconda is a Python Nagios wrapper.",
      long_description=NagAconda.__doc__,
      author='Shaun Thomas',
      author_email='sthomas@leapfrogonline.com',
      url='http://www.leapfrogonline.com/',
      packages=['NagAconda'],
      tests_require=['nose>=0.11',],
      install_requires=['Sphinx'],
      test_suite = 'nose.collector',
     )
