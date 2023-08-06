#!/usr/bin/env python
# encoding: utf-8
"""
setup.py for pyMessaging

Created by Maximillian Dornseif on 2007-08-08.
Copyright (c) 2007 HUDORA GmbH. Consider it BSD licensed.
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name='pyMessaging',
      version='0.3',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='http://cybernetics.hudora.biz/dist/pyMessaging/',
      description='Message Passing Framework for Python.',
      long_description='pyMessaging 0.3 only implements Twitter. Earlier Versions implemented STOMP.',
      license='BSD',
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python'],
      packages = find_packages()
      )
