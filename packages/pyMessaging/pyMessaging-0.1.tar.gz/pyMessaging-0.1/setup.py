#!/usr/bin/env python
# encoding: utf-8
"""
setup.py for pyMessaging

Created by Maximillian Dornseif on 2007-08-08.
Copyright (c) 2007 HUDORA GmbH. Consider it BSD licensed.
"""

from distutils.core import setup
setup(name='pyMessaging',
      version='0.1',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='http://www.hudora.de/code/',
      description='Message Passing Framework for Python implementing somewhat JMS-like semantics.',
      long_description='pyMessaging at the moment only implements the Stomp protocol. Try "pydoc pyMessaging.stomp" for further explanation.',
      license='BSD',
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python'],
      package_dir = {'pyMessaging': ''},
      packages=['pyMessaging'],
      scripts=['bin/pymessaging_read'],
      install_requires = ['simplejson'],
      )
