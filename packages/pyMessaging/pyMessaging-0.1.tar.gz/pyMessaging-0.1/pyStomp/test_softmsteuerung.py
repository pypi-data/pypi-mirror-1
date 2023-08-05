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
import asyncore
from pySoftM.screenscraping import SoftMremote
from pyMessaging.pyStomp import StompSender, StompReader, MessageHandler

HOST = 'broker.local.hudora.biz'
PORT = 61613

class MPLFreigabeHandler(MessageHandler):
    def recv_message(self, headers, body):
        """Gibt einen Vorgang im SoftM MPL frei."""
        vorgangsnummer = body.split(':')[0]
        print repr((vorgangsnummer, headers, body))
        s = SoftMremote()
        s.umlagerung_freigeben(str(int(vorgangsnummer)))
        
class MPLRueckmeldeHandler(MessageHandler):
    """Meldet einen Vorgang im SoftM MPL komplett zurück."""
    def recv_message(self, headers, body):
        vorgangsnummer = body.split(':')[0]
        print repr((vorgangsnummer, headers, body))
        s = SoftMremote()
        s.umlagerung_rueckmelden(str(int(vorgangsnummer)))

class LieferscheinRueckmeldeHandler(MessageHandler):
    """Meldet einen Lieferschein in einem SoftM Blocklager zurück."""
    def recv_message(self, headers, body):
        lieferscheinnummer = body.split(':')[0]
        print repr((lieferscheinnummer, headers, body))
        s = SoftMremote()
        s.umlagerung_rueckmelden(str(int(vorgangsnummer)))
        
class AuftragsImportHandler(MessageHandler):
    """Startet den Import der Auftrags-Stapelschnittstelle in SoftM."""
    def recv_message(self, headers, body):
        print repr((headers, body))
        s = SoftMremote()
        s.stapelimport()
        
class PingHandler(MessageHandler):
    def recv_message(self, headers, body):
        global s
        print repr((headers, body))
        s.send_message(headers['reply-to'], repr((headers, body)), headers={'correlation-id': headers['message-id']})
        s.send_message(headers['reply-to'], 'DROPME')
        print "done sending"

def main():
    global s
    s = StompReader((HOST, PORT),
                    handlers=[MPLFreigabeHandler('/queue/erp.warenbewegung.vorgangsfreigabe'),
                              MPLRueckmeldeHandler('/queue/erp.warenbewegung.vorgangsrueckmeldung'),
                              LieferscheinRueckmeldeHandler('/queue/erp.warenbewegung.lieferscheinrueckmeldung'),
                              AuftragsImportHandler('/queue/erp.stapelschnittstelle.auftraege.befuellt'),
                              PingHandler('/queue/admin.ping'),
                              ])
    asyncore.loop()

    
if __name__ == '__main__':
    main()
    # unittest.main()
