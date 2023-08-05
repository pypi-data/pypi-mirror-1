#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Maximillian Dornseif on 2007-04-09.
Copyright (c) 2007 HUDORA GmbH. Consider it BSD licensed.

My rough attempts in implementing the Stomp protocol. Tested with Apache AcitveMQ.
See http://stomp.codehaus.org/ for more Information on Stomp.
"""

import sys, os, unittest, time
import socket
from pySoftM.screenscraping import SoftMremote


HOST = 'broker.local.hudora.biz'
PORT = 61613

    
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.send('CONNECT\n\n\x00\n')
    reply = sock.recv(9999)
    if not reply.startswith('CONNECTED\nsession:'): # ActiveMX is not sending the space after 'session:'
        raise RuntimeError, 'Invalid server reply: %r' % reply
    # sock.send('SUBSCRIBE\ndestination: /topic/huLOG.warenbewegung.out.gatescan\nack: auto\n\n\x00\n')
    sock.send('SUBSCRIBE\ndestination: /queue/ERP.warenbewegung.vorgangsfreigabe\nack: auto\n\n\x00\n')
    print "subscribed"
    reply = ''
    while True:
        while not reply.endswith('\x00\n'):
            reply = sock.recv(9999)
            if not reply.startswith('MESSAGE\n'):
                raise RuntimeError, 'Invalid server reply: %r' % reply
        header = reply.split('\n\n')[0]
        body = '\n\n'.join(reply.split('\n\n')[1:])
        # MESSAGE
        # destination:/topic/huLOG.warenbewegung.in.gatescan
        # receipt:msgid-172413296-1177318922.781874
        # timestamp:1177315079743
        # priority:0
        # expires:0
        # message-id:ID:hurricane.local.hudora.biz-56940-1176409517146-5:19701:-1:1:1
        # 
        # 61605:warenausgang: Gatescan-In
        print repr(body)
        vorgangsnummer = body.split(':')[0]
        print repr(vorgangsnummer)
        s = SoftMremote()
        s.umlagerung_freigeben(str(int(vorgangsnummer)))
        reply = ''
        
                
    sock.send('DISCONNECT\n\x00\n')

    
if __name__ == '__main__':
    main()
    # unittest.main()
