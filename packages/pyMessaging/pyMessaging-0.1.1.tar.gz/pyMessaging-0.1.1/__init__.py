#!/usr/bin/env python
# encoding: utf-8
"""
pyMessaging - Framework to use messaging functionality along the lines of JMS.

Currently only the Stomp Protocol is suported. But the pyMessaging framework
tries to be transport agnostic.

Based on transport Protocols we implement a slightly higher level protocol for
more complex messages.

Most lower-level protocos provide us with a concept of a set ofr headers and a
message body, whereas the body is considered a opaque string of bytes (or
octets if you are old school.)

pyMessaging body to swtore more complex message objects and possibly at one
time implement features like message compression and fragmentation.

The functionality of the upper layer is imlemented in messaging.py

Created by Maximillian Dornseif on 2007-04-09.
Copyright (c) 2007 HUDORA GmbH. Consider this BSD licensed.
"""

from messaging import send_bytes, send_message

__revision__ = "$Revision: 2281 $"
