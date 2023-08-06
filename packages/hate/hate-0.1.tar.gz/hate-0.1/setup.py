#!/usr/bin/env python

from distutils.core import setup

setup(name='hate',
      version='0.1',
      description='High Availability Terminal Emulator',
      author='Stephen Thorne',
      author_email='stephen@thorne.id.au',
      url='https://launchpad.nb/hate',
      packages=['hate'],
      package_data={'hate': ['*.svg']},
      scripts=['bin/hate'],
     )

