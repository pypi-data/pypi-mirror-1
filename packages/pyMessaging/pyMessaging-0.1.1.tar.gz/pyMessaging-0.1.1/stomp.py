#!/usr/bin/env python
# encoding: utf-8
"""
stomp.py - Implementation of the STOMP messaging protocol.

My rough attempts in implementing the Stomp protocol. Tested with Apache
AcitveMQ. See http://stomp.codehaus.org/ for more Information on Stomp.

Unfortunately I was not able to make this completely reliable. I suspect this
is not not only this libraries problem but also an issue within ActiveMQs
Stomp implementation. Within certain limits it works reliable. Search the
comments in test_stomp.py for LENSTEPS in this file to get an idea where the
limits are.

The module is centered arround the StompConnection class with it's main
interface beeing

 * send_message()
 * subscribe()
 * receive_message()

In addition there is the convinience method receive_bytes() which discards
message headers returned from receive_message and leaves only the message
body. In addition there are the module level convinience functions
send_message(), receive_messages() and receive_byte_messages() which offer an
not object oriented interface to the Stomp protocol.

>>> msgid = send_message('/queue/TEST/stomp.py', 'Hello.world!')
>>> get_message_bodies('/queue/TEST/stomp.py')
['Hello.world!']

>>> msgid = send_message('/queue/TEST/stomp.py', 'Again: Hello.world!')
>>> headers, body = get_messages('/queue/TEST/stomp.py')[0]
>>> headers['message-id'] == msgid
True
>>> body
'Again: Hello.world!'

See StompConnection.__init__() for documentation on how the address of the
broker is selected.

This module comes with some unittests. Make sure you have a Stomp broker
running on localhost:61613 and call python stomp.py to run the tests.

Created by Maximillian Dornseif on 2007-04-09.
Copyright (c) 2007 HUDORA GmbH. Consider it BSD licensed.

"""

import time, os, socket, random

__revision__ = "$Revision: 2281 $"

DEFAULTHOST = 'localhost'
DEFAULTPORT = 61613
BUFSIZE = 4096
DEBUG = False

# run connections in "ack: client" or "ack: auto" mode?
# Seemingly ActiveMQ 5.0-20070812.222711-51 can not handle ack: client.
ACKMODE = 'auto'

class StompException(Exception):
    """Base class for exception raised by this module."""
    pass
    
class StompProtocolException(StompException):
    """Exceptions which a caused by issues in communication with the server."""
    pass

class StompConnection(object):
    """Object-oriented Interface representing a Stomp connection."""
    
    def __init__(self, host=None, port=None):
        """Initiates a Stomp Connection defined by host and port. If host and
           port are not given, we check the environment variable STOMPBROKER
           expecting something like 'broker.example.com:61613'.
           """
          
        self.ibuffer = ['']
        self.incomming_messags = []
        self.subscriptions = {}
        self.host = host
        self.port = port
        self.closed = False
        if not self.host:
            if os.environ.get('STOMPBROKER'):
                self.host = os.environ.get('STOMPBROKER').split(':')[0]
            else:
                self.host = DEFAULTHOST
        if not self.port:
            if os.environ.get('STOMPBROKER'):
                self.port = os.environ.get('STOMPBROKER').split(':')[1]
            else:
                self.port = DEFAULTPORT
        self._connect()
    
    
    def __del__(self):
        # Destructor: sends a DISCONNECT frame out of courtesy.
        if not self.closed:
            self._push('DISCONNECT\n\x00\n')
            self.sock.close()
    
    
    def close(self):
        """Disconnect from the Server. No further communication is possible
           afterwards."""
        
        if self.closed:
            raise RuntimeError, 'tried to close connection twice'
        self._push('DISCONNECT\n\x00\n')
        self.sock.close()
        self.closed = True
    
    
    def _push(self, data):
        """Send data via the socket taking into consideration short write issues."""
        
        while data:
            shippedbytes = self.sock.send(data)
            if DEBUG:
                print "%08x >>> %r" % (id(self.sock), data[:shippedbytes])
            data = data[shippedbytes:]
    
    
    def _pull(self, maxbytes=BUFSIZE):
        """Read maxbytes or less from the socket, possibly blocking.
        
        Be aware that _pull might return less than maxbytes."""
        ret = self.sock.recv(maxbytes)
        if DEBUG:
            print "%08x <<< %r" % (id(self.sock), ret)
        return ret
    
    
    def _read_bytes(self, numbytes):
        """Read at least numbytes. Blocking."""
        
        data = ''.join(self.ibuffer)
        while len(data) < numbytes:
            data += self._pull()
        self.ibuffer = [data[numbytes:]]
        return data[:numbytes]
    
    
    def _read_until_0(self):
        """Read until we at least encounter a \0. Blocking."""
        
        while (not self.ibuffer) or '\0' not in self.ibuffer[-1]:
            self.ibuffer.append(self._pull())
        data = ''.join(self.ibuffer)
        pos0 = data.index('\0')
        self.ibuffer = [data[pos0:]]
        return data[:pos0]
    
    
    def _read_header(self, timeout=0):
        """Read a command and a header - could also be called read_until_NL_NL. Blocking."""
        
        while (not self.ibuffer) or '\n\n' not in self.ibuffer[-1]:
            if timeout:
                self.sock.settimeout(timeout)
            self.ibuffer.append(self._pull())
        data = ''.join(self.ibuffer)
        headers, remainder = data.split('\n\n', 1)
        self.ibuffer = [remainder]
        return headers
    
    
    def _connect(self):
        """Connect to Broker."""
        
        # unfortunately ths occasionally fails with 5.0-20070812.222711-51
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(120)
        self.sock.connect((self.host, int(self.port)))
        self._push('CONNECT\n\n\x00\n')
        reply, headers, body = self._read_frame()
        if not reply == 'CONNECTED':
            raise RuntimeError, 'Invalid server reply: %r' % ((reply,  headers, body),)
        self.subscriptions = {}
    
    
    def _read_frame(self, timeout=0):
        """Read the next incomming frame."""
        
        # read data and remove whitespace inserted by ActiveMQ
        headerdata = self._read_header(timeout=timeout).lstrip()
        
        command, headers = headerdata.split('\n', 1)
        headers = [x.split(':', 1) for x in headers.split('\n')]
        headers = dict([(x[0], x[1].lstrip()) for x in headers])
        
        # we use totaly different code paths for handling frames containing content-length and others
        if headers.get('content-length'):
            body = self._read_bytes(int(headers.get('content-length')))
        else:
            body = self._read_until_0()
        # clean up remainder of frame left in ibuffer
        self.ibuffer = [''.join(self.ibuffer)]
        if not self.ibuffer[0] or (self.ibuffer[0][0] is not '\0'):
            raise StompException, "Something fishy - missing NUL: %r" % (self.ibuffer,)
        else:
            self.ibuffer[0] = self.ibuffer[0][1:]
        # put unused data back in the buffer removing leading whitespace introduced by ActiveMQ
        self.ibuffer[0] = self.ibuffer[0].lstrip()
        # clean up begining of the reminder
        return (command, headers, body)
    
    
    def subscribe(self, destination):
        """Subscribes to a destination.
        
        Returns a subscription-id which is also found in the headers of
        messages received via this connection.
        
        >>> s = StompConnection()
        >>> subid = s.subscribe('/topic/TEST')
        """
        
        subid = 'sub-%x-%f%s' % (id(destination), time.time(), destination.replace('/', '.'))
        self._push(('SUBSCRIBE\ndestination: %s\nack: %s\nactivemq.prefetchSize: 1\n' \
                    + 'activemq.dispatchAsync: true\nid: %s\n\n\x00\n') % (destination, ACKMODE, subid))
        self.subscriptions[subid] = destination
        return subid
    
    
    def receive_message(self, timeout=0.01):
        """Recieve a message from the connection.
        
        Returns (None, None) if it wasn't able to read data for 'timeout'
        seconds. The message returned consists of 
        ({header1: 'val1', header2: 'val2}, body).
        """
        
        # TODO: check what happens when an timeut occures inbetween reading header and body.
        try:
            command, headers, body = self._read_frame(timeout=timeout)
        except socket.timeout:
            return None, None
        if not command:
            return None, None
        if command == 'MESSAGE':
            if ACKMODE == 'client':
                # send ACK
                self._push('ACK\nmessage-id:%s\n\n\x00\n' % (headers['message-id'],))
        else:
            raise StompProtocolException, 'Expected MESSAGE but got %r' % ((command, headers, body),)
        return headers, body
    
    
    def receive_bytes(self, timeout=0.01):
        """Recieve the body of a message from the connection.
        
        Returns None if it wasn't able to read data for 'timeout' seconds. """
        
        return self.receive_message(timeout)[1]
    
    
    def send_message(self, dest, msg, priority=5, headers={}, recursion_allowed=True):
        """Send a message on the open Stop connection.
        
        >>> s = StompConnection()
        >>> msgid = s.send_message('/topic/TEST', 'data')
        """
        
        msgid = 'pyStompID-%x-%f-%x' % (id(msg), time.time(), random.getrandbits(31))
        receiptid = 'rcpt#' + msgid
        lineheaders = {'priority': str(priority),
                       'persistent': 'true',
                       'destination': str(dest),
                       'message-id': msgid,
                       'receipt': receiptid,
                       }
        lineheaders.update(headers)
        lineheaderstr = '\n'.join([('%s: %s' % x) for x in lineheaders.items()])
        if lineheaderstr:
            lineheaderstr = '\n' + lineheaderstr
        try:
            if '\0' in msg:
                self._push('SEND%s\ncontent-length:%d\n\n%s\x00\n' % (lineheaderstr, len(msg), msg))
            else:
                self._push('SEND%s\n\n%s\x00\n' % (lineheaderstr, msg))
        except socket.error, msg:
            # TODO: sensible logging
            print '+++ Reconnecting!', msg
            # reopen and retry
            if recursion_allowed:
                self._connect()
                # TODO: we have to resubscribe
                self.send_message(dest, msg, priority, recursion_allowed=False)
            else:
                raise
        # check for RECIEPT
        command, headers, body = self._read_frame(timeout=10)
        # a successfull reciept has the correct id and an empty body
        if command != 'RECEIPT':
            raise StompProtocolException, "Message %r, unexpected reply COMMAND: %r\n%r\n%s" \
                                           % (msgid, command, headers, body)
        if headers.get('receipt-id') != receiptid:
            raise StompProtocolException, "Message %r, unexpected reply id: %r\n%r\n%s" \
                                           % (msgid, command, headers, body)
        if body != '':
            raise StompProtocolException, "Message %r, unexpected reply body: %r\n%r\n%r" \
                                           % (msgid, command, headers, body)
        return lineheaders['message-id']


def send_message(destination, msg, priority=5, headers={}):
    """Send a message to destination.
    
    >>> msgid = send_message('/topic/TEST', 'data')
    """
    
    conn = StompConnection()
    return conn.send_message(destination, msg, priority, headers)


def get_messages(destination, host=None, port=None, timeout=0.1, maxmessages=None):
    """Read all available messages from the queue 'destination'.
    
    If maxmessages is set, don't read more than 'maxmessages' messages.
    
    >>> get_messages('/topic/TEST/empty')
    []
    """
    ret = []
    conn = StompConnection(host, port)
    conn.subscribe(destination)
    while True:
        message = conn.receive_message(timeout=timeout)
        if message == (None, None) or (maxmessages and len(ret) >= maxmessages):
            break
        ret.append(message)
    return ret

def get_message_bodies(destination, host=None, port=None, timeout=0.1, maxmessages=None):
    """Read all available message bodies from the queue 'destination'.
    
    >>> get_message_bodies('/topic/TEST/empty')
    []
    """
    
    return [x[1] for x in get_messages(destination, host, port, timeout, maxmessages)]


if __name__ == '__main__':
    import doctest
    if not DEBUG:
        doctest.testmod()
    from test_stomp import *
    # flush queues
    for part in ('', '/A', '/B', '/C', '/D', '/E', '/F'):
        get_messages('/queue/TEST%s' % part)
    unittest.main()
    # flush queues
    for part in ('', '/A', '/B', '/C', '/D', '/E', '/F'):
        get_messages('/queue/TEST%s' % part)

