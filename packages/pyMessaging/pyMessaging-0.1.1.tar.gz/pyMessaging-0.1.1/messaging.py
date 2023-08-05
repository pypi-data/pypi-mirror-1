#!/usr/bin/env python
# encoding: utf-8
"""

messaging.py - implements high-level functions in pyMessaging constructing
messages to be send over lower layers. At the moment pyStomp is the only
supported lower layer. See pyMessaging.stomp for a description of how the
appropriate broker (hint: 'export STOMPBROKER=broker.example.com:61613')
and pyMessaging.__init__ for more high level
documentation.

Created by Maximillian Dornseif on 2007-04-09.
Copyright (c) 2007 HUDORA GmbH. Consider this BSD licensed.
"""

import simplejson, os
import stomp

__revision__ = "$Revision: 2281 $"

def send_bytes(destination, bytes, priority=5, headers={}):
    """Sent a message of bytes without furter modification.
    
    Returns a message-id.
    
    >>> msgid = send_bytes('/topic/TEST', 'SomeBytes')
    """
    return stomp.send_message(destination, bytes, priority=5, headers={})

def send_message(destination, priority=5, headers={}, **kwargs):
    """Send a structured message using the pyMessaging format.
    
    Returns a message-id.
    
    >>> msgid = send_message('/topic/TEST', key1='val1', key2='val2')
    """
    # protocol-format 1: JSON
    data = '1' + simplejson.dumps(kwargs)
    return stomp.send_message(destination, data, priority=5, headers={})


if __name__ == '__main__':
    import doctest
    doctest.testmod()
