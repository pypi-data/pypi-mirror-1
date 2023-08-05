#!/usr/bin/env python
# encoding: utf-8
"""
Created by Maximillian Dornseif on 2007-04-09.
Copyright (c) 2007 HUDORA GmbH. Consider it BSD licensed.

My rough attempts in implementing the Stomp protocol. Tested with Apache AcitveMQ.
See http://stomp.codehaus.org/ for more Information on Stomp.
"""

import sys, os, unittest, time
import socket

HOST = 'broker.local.hudora.biz'
PORT = 61613

class StompSender(object):
    def __init__(self):
        self.connect()
    
    def __del__(self):
        self.sock.send('DISCONNECT\n\x00\n')
        self.sock.close()
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.sock.send('CONNECT\n\n\x00\n')
        reply = self.sock.recv(4096)
        if not reply.startswith('CONNECTED\nsession:'): # ActiveMX is not sending the space after 'session:'
            raise RuntimeError, 'Invalid server reply: %r' % reply
    
    def send_message(self, dest, msg, priority=5, headers={}, recursion_allowed=True):
        msgid = 'pyStompID-%s-%f' % (id(msg), time.time())
        lineheaders = {'priority': str(priority),
                       'persistent': 'true',
                       'destination': str(dest),
                       'message-id': msgid,
                       }
        lineheaders.update(headers)
        lineheaderstr = '\n'.join([('%s: %s' % x) for x in lineheaders.items()])
        if lineheaderstr:
            lineheaderstr = '\n' + lineheaderstr
        try:
            if '\0x00' in msg:
                self.sock.send('SEND\n%scontent-length:%d\n\n%s\x00\n' % (lineheaderstr, len(msg), msg))
            else:
                self.sock.send('SEND%s\n\n%s\x00\n' % (lineheaderstr, msg))
        except socket.error, msg:
            print msg
            # reopen and retry
            if recursion_allowed:
                self.connect()
                self.send_message(dest, msg, priority, recursion_allowed=False)
            else:
                raise

def stompRPC(dest, msg):
    s = StompSender()
    msgid = 'pyStompRPC-%s-%f' % (id(msg), time.time())
    # replyto = '/temp-queue/%s' % (dest.lstrip('/').replace('/', '.'))
    # if /queue/ is used instead /temp-queue/ the whole thing works
    replyto = '/queue/%s' % (dest.lstrip('/').replace('/', '.'))
    print 'sending to %r, expecting reply at %r' % (dest, replyto)
    s.send_message(dest, msg, priority=5, headers={'reply-to': replyto, 'message-id': msgid,})
    print "subscribing %r" % replyto
    s.sock.send("SUBSCRIBE\ndestination: %s\nack: auto\n\n\x00\n" % (replyto))
    ret = []
    # s.sock.settimeout(0.1)
    reply = _read_until_0(s.sock).strip()
    trailing = s.sock.recv(1)
    print "XXX", repr(reply)
    if not reply.startswith('MESSAGE\ndestination:%s\n' % replyto):
        raise RuntimeError, 'Invalid server reply: %r' % reply
    message = '\n\n'.join(reply.split('\n\n')[1:])
    ret.append(message.strip('\n\0\r'))
    return ret
    

def _read_until_0(sock):
    ret = []
    ret.append(sock.recv(1))
    while ret[-1] != '\0':
        ret.append(sock.recv(1))
    return ''.join(ret)
    
def get_messages(channel):
        ret = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.send('CONNECT\n\n\x00\n')
        reply = sock.recv(9999)
        if not reply.startswith('CONNECTED\nsession:'): # ActiveMX is not sending the space after 'session:'
            raise RuntimeError, 'Invalid server reply: %r' % reply
        sock.send('SUBSCRIBE\ndestination: %s\nack: auto\nactivemq.prefetchSize: 1\n' \
                          + 'activemq.dispatchAsync: true\n\n\x00\n' % (channel))
        sock.settimeout(0.1)
        while True:
            try:
                reply = _read_until_0(sock).strip()
                trailing = sock.recv(1)
            except socket.timeout:
                break
            if not reply.startswith('MESSAGE\ndestination:%s\n' % channel):
                raise RuntimeError, 'Invalid server reply: %r' % reply
            message = '\n\n'.join(reply.split('\n\n')[1:])
            print "XXX", repr(reply)
            ret.append(message.strip('\n\0\r'))
        sock.send('DISCONNECT\n\x00\n')
        return ret


class tmpTests(unittest.TestCase):
    def test_rpc(self):
        start = time.time()
        print stompRPC('/queue/test.bouncer', 'XXXtestBodyXXX')
        end = time.time()
        print "stompRPC(): %.5fs" % (end-start)
    
if __name__ == '__main__':
    #print '\n'.join(get_messages('/queue/erp.stammdaten.keinpalettenfaktor'))
    # /temp-queue/ /temp-topic/
    unittest.main()
    