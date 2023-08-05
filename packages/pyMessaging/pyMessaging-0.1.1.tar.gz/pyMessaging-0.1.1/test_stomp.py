#!/usr/bin/env python
# encoding: utf-8
"""
test_stomp.py - Tests for stomp.py.

See stomp.py for further documentation.

Created by Maximillian Dornseif on 2007-04-09.
Copyright (c) 2007 HUDORA GmbH. Consider it BSD licensed.

"""

import unittest, random
from stomp import StompConnection, send_message, get_messages, get_message_bodies, StompProtocolException

__revision__ = "$Revision: 2281 $"

# the paramers bllow work most of the bime. set the values higher and ActiveMQ breaks down
# try 2**(2*LENSTEPS) as maximum message size
LENSTEPS = 5
# try this amount of messages at once
COUNTSTEPS = 50
# how many connections to be tried at once
CONCURRENTCONNECTIONS = 10

# this set of parameters at least sometimes works
#(LENSTEPS, COUNTSTEPS, CONCURRENTCONNECTIONS) = (9, 230, 40)

# the parameters below result nearly always in failures
#(LENSTEPS, COUNTSTEPS, CONCURRENTCONNECTIONS) = (12, 300, 40)

class SendMessageTests(unittest.TestCase):
    """Tests for sending messages - we just don't care where the messages go."""
    def setUp(self):
        self.destination = '/topic/TEST'
    
    
    def test_send_message(self):
        send_message(self.destination, 'data')
        send_message(self.destination, 'data', priority=5)
        send_message(self.destination, 'data', headers={'foobar': 'stuff:fluff'})
        send_message(self.destination, 'data\0data')
        send_message(self.destination, 'data\0data', priority=5)
        send_message(self.destination, 'data\0data', headers={'foobar': 'stuff:fluff'})
    
    
    def test_msgid_overwrite(self):
        s = StompConnection()
        returnval = s.send_message(self.destination, 'data')
        self.assertEqual('pyStompID-', returnval[:10])
        msgid = '2-1-2-this_is_just_a_test'
        returnval = s.send_message(self.destination, 'data', headers={'message-id': msgid})
        self.assertEqual(msgid, returnval)
    
    
    def test_send_message_obj(self):
        s = StompConnection()
        s.send_message(self.destination, 'data')
        s.send_message(self.destination, 'data', priority=5)
        s.send_message(self.destination, 'data', headers={'foobar': 'stuff:fluff'})
        s.send_message(self.destination, 'data\0data')
        s.send_message(self.destination, 'data\0data', priority=5)
        s.send_message(self.destination, 'data\0data', headers={'foobar': 'stuff:fluff'})
    
    
    def test_invalid_destination(self):
        s = StompConnection()
        self.assertRaises(StompProtocolException, s.send_message, '/invalid', 'data')
        self.assertRaises(StompProtocolException, s.send_message, '/invalid2', 'data')
        self.assertRaises(StompProtocolException, s.send_message, '/invalid', 'data\0data')
        self.assertRaises(StompProtocolException, s.send_message, '/invalid2', 'data\0data')
        self.assertRaises(StompProtocolException, send_message, '/invalid', 'data')
    
    
    def test_send_strange_data(self):
        s = StompConnection()
        for data in ['TEST', '\0test', '\0test', 'te\0st', '\n', '\0', '', '\r\n', '\n\n\n\n']:
            s.send_message(self.destination, data)
    
    
    def test_sizes(self):
        s = StompConnection()
        for lenfact in range(LENSTEPS):
            datalen = 2**(lenfact*2)
            data = ('%d:%d:' % (lenfact, datalen)) + ('X' * (datalen))
            s.send_message(self.destination, data)
            data = ('\0%d:%d:' % (lenfact, datalen)) + ('X' * (datalen)) + '\0'
            s.send_message(self.destination, data)
        
    
class SendMessageTestsQueue(SendMessageTests):
    """Tests for sending messages - we just don't care where the messages go."""
    def setUp(self):
        self.destination = '/queue/TEST/A'
        # flush queue
        get_messages(self.destination)
    
    def tearDown(self):
        # flush queue
        get_messages(self.destination)

class TestMannyConnections(unittest.TestCase):
    def setUp(self):
        self.destination = '/topic/TEST'
    
    def test_manywriters1(self):
        rconn = StompConnection()
        rconn.subscribe(self.destination)
        wconns = []
        for i in range(CONCURRENTCONNECTIONS):
            wconns.append(StompConnection())
        for i in range(CONCURRENTCONNECTIONS*2):
            random.choice(wconns).send_message(self.destination, str(i))
        # ActiveMQ 5.0-20070812.222711-51 doesnot retain the ordering in which the messages are sent
        allretvals = []
        for i in range(CONCURRENTCONNECTIONS*2):
            allretvals.append(rconn.receive_bytes())
        for i in range(CONCURRENTCONNECTIONS*2):
            self.assertTrue(str(i) in allretvals)

    def test_manywritersordered(self):
        rconn = StompConnection()
        rconn.subscribe(self.destination)
        wconns = []
        for i in range(CONCURRENTCONNECTIONS):
            wconns.append(StompConnection())
        for i in range(CONCURRENTCONNECTIONS*2):
            random.choice(wconns).send_message(self.destination, str(i))
        # ActiveMQ 5.0-20070812.222711-51 does not retain the ordering in which the messages are sent
        retvals = []
        for i in range(CONCURRENTCONNECTIONS*2):
            retvals.append(rconn.receive_bytes())
        for i in range(CONCURRENTCONNECTIONS*2):
            self.assertTrue(str(i) in retvals)
    
#     # does not work with ActiveMQ 5.0-20070812.222711-51 because of the order in wich sockets are opened
#     def test_manywriters2(self):
#         wconns = []
#         for i in range(CONCURRENTCONNECTIONS):
#             wconns.append(StompConnection())
#         rconn = StompConnection()
#         rconn.subscribe(self.destination)
#         for i in range(CONCURRENTCONNECTIONS*2):
#             random.choice(wconns).send_message(self.destination, str(i))
#         for i in range(CONCURRENTCONNECTIONS*2):
#             self.assertEqual(str(i), rconn.receive_bytes())
        
    
#     # does not work with ActiveMQ 5.0-20070812.222711-51 because of the order in wich sockets are opened
#     def test_manywriters3(self):
#         rconn = StompConnection()
#         wconns = []
#         for i in range(CONCURRENTCONNECTIONS):
#             wconns.append(StompConnection())
#         rconn.subscribe(self.destination)
#         for i in range(CONCURRENTCONNECTIONS*2):
#             random.choice(wconns).send_message(self.destination, str(i))
#         for i in range(CONCURRENTCONNECTIONS*2):
#             self.assertEqual(str(i), rconn.receive_bytes())
        
class TestMannyConnectionsQueue(TestMannyConnections):
    def setUp(self):
        self.destination = '/queue/TEST/B'
        # flush queue
        get_messages(self.destination)
    
    def tearDown(self):
        # flush queue
        get_messages(self.destination)
    
    def read_all_data_from_connections(self, connections):
        # pull data from all the connections - we assume that there is no completely even distribution
        ret = []
        while True:
            retvals = set()
            for rconn in connections:
                ret.append(rconn.receive_bytes())
                retvals.add(ret[-1])
                if ret[-1] and not ret[-1].isdigit():
                    print 'unexpected return value %r on connection %r' % (ret[-1], rconn)
            if retvals == set([None]):
                # nothing new found
                break
        return ret
    
    
    def test_manyreaders(self):
        """Check the distribution on a queue to many readers."""
        # open many connectins and make them subscribe
        rconns = []
        for i in range(CONCURRENTCONNECTIONS):
            rconns.append(StompConnection())
            rconns[-1].subscribe(self.destination)
        # open a writer and write CONCURRENTCONNECTIONS*2 messages
        wconn = StompConnection()
        for i in range(CONCURRENTCONNECTIONS*2):
            wconn.send_message(self.destination, str(i))
        # pull data from all the connections - we assume that there is no completely even distribution
        retvals = self.read_all_data_from_connections(rconns)
        # check that we received all messages we actually have sent
        for i in range(CONCURRENTCONNECTIONS*2):
            self.assertTrue(str(i) in retvals)


class TestsSendReceiveASCII(unittest.TestCase):
    def setUp(self):
        # CARVE! the order in wich sockets re opened influence ActiveMQs operation
        self.destination = '/topic/TEST'
        self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
        self.wconn = StompConnection()
    
    
    def test_turnarround(self):
        for data in ['TT', '', '\n', '\r\n', '\n\n\n\n', 'test']:
            self.wconn.send_message(self.destination, 'simple1')
            self.assertEqual('simple1', self.rconn.receive_bytes())
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())
            self.wconn.send_message(self.destination, 'simple2')
            self.assertEqual('simple2', self.rconn.receive_bytes())
    
    
    def test_queue_fill(self):
        for num in range(COUNTSTEPS):
            self.wconn.send_message(self.destination, str(num))
        for num in range(COUNTSTEPS):
            self.assertEqual(str(num), self.rconn.receive_bytes())
    
    
    def test_queue_fill(self):
        for num in range(COUNTSTEPS):
            self.wconn.send_message(self.destination, str(num))
            self.assertEqual(str(num), self.rconn.receive_bytes())
    
    
    def test_sizes(self):
        for lenfact in range(LENSTEPS):
            datalen = 2**(lenfact*2)
            # Simple message meant as framing for the big message
            data = "simple1 %2d %d" % (lenfact, datalen)
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())
            
            # Pure ASCII Test Message
            data = ('%d:%d:' % (lenfact, datalen)) + ('X' * datalen)
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())
            
            # Simple message meant as framing for the big message
            data = "simple2 %2d %d" % (lenfact, datalen)
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())
    

class TestsSendReceiveASCIIQueue(unittest.TestCase):
    def setUp(self):
        # CARVE! the order in wich sockets re opened influence ActiveMQs operation
        self.destination = '/queue/TEST/C'
        # flush queue
        get_messages(self.destination)
        self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
        self.wconn = StompConnection()
        
    def tearDown(self):
        self.rconn.close()
        self.wconn.close()
        # flush queue
        get_messages(self.destination)
    
#     # ActiveMQ 5.0-20070812.222711-51 does not retain the ordering in which the messages are sent
#     def test_write_close_read_ordered(self):
#         for i in range(COUNTSTEPS):
#             self.wconn.send_message(self.destination, str(i))
#         for i in range(COUNTSTEPS):
#             self.assertEqual(str(i), self.rconn.receive_bytes())
    
    def test_write_close_read(self):
        for i in range(COUNTSTEPS):
            self.wconn.send_message(self.destination, str(i))
        retvals = []
        for i in range(COUNTSTEPS):
            retvals.append(self.rconn.receive_bytes())
            if (not retvals[-1]) or not (retvals[-1].isdigit()):
                print 'unexpected return value %r on connection %r' % (retvals[-1], self.rconn)
        # check that we received all messages we actually have sent
        for i in range(COUNTSTEPS):
            self.assertTrue(str(i) in retvals)


class TestsSendReceiveBinary(unittest.TestCase):
    def setUp(self):
        # CARVE! the order in wich sockets are opened influence ActiveMQs operation
        self.destination = '/topic/TEST'
        self.wconn = self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
    
    
    def tearDown(self):
        self.rconn.close()
        # flush queue
        get_messages(self.destination)
    
    
    def test_turnarround(self):
        for data in ['test\0', 'te\0st', '\0test', '\0', '\n\0', '\0\0', '\0\n', '\0\n\0']:
            self.wconn.send_message(self.destination, 'simple1')
            self.assertEqual('simple1', self.rconn.receive_bytes())
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())
            self.wconn.send_message(self.destination, 'simple2')
            self.assertEqual('simple2', self.rconn.receive_bytes())
    
    
class TestsSendReceiveBinaryQueue(unittest.TestCase):
    def setUp(self):
        # CARVE! the order in wich sockets are opened influence ActiveMQs operation
        self.destination = '/queue/TEST/D'
        # flush queue
        get_messages(self.destination)
        self.wconn = self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
    
    def tearDown(self):
        self.rconn.close()
        self.wconn.close()
        # flush queue
        get_messages(self.destination)
    
    
class TestsSendReceiveBinary1(TestsSendReceiveBinary):
    def setUp(self):
        # CARVE! the order in wich sockets re opened influence ActiveMQs operation
        self.destination = '/topic/TEST'
        # flush queue
        get_messages(self.destination)
        self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
        self.wconn = StompConnection()
    
    
    def test_sizes(self):
        for lenfact in range(LENSTEPS):
            datalen = 2**(lenfact*2)
            
            # Simple message meant as framing for the big message
            data = "simple1 %2d %d" % (lenfact, datalen)
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())
            
            # Test Message containing \0
            data = ('\0%d:%d:' % (lenfact, datalen) + ('X' * datalen)) + '\0'
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())
            
            # Simple message meant as framing for the big message
            data = "simple2 %2d %d" % (lenfact, datalen)
            self.wconn.send_message(self.destination, data)
            self.assertEqual(data, self.rconn.receive_bytes())

    
class TestsSendReceiveBinary1Queue(TestsSendReceiveBinary):
    def setUp(self):
        # CARVE! the order in wich sockets re opened influence ActiveMQs operation
        self.destination = '/queue/TEST/E'
        # flush queue
        get_messages(self.destination)
        self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
        self.wconn = StompConnection()
    
    
    def tearDown(self):
        self.rconn.close()
        self.wconn.close()
        # flush queue
        get_messages(self.destination)
    

# class TestsSendReceiveBinary2(TestsSendReceiveBinary):
#     # does not work with ActiveMQ 5.0-20070812.222711-51 because of the order in wich sockets are opened
#     def setUp(self):
#         self.destination = '/topic/TEST'
#         self.wconn = StompConnection()
#         self.rconn = StompConnection()
#         self.rconn.subscribe(self.destination)

# class TestsSendReceiveBinary3(TestsSendReceiveBinary):
#     # does not work with ActiveMQ 5.0-20070812.222711-51 because of the order in wich sockets are opened
#     def setUp(self):
#         self.destination = '/topic/TEST'
#         self.rconn = StompConnection()
#         self.wconn = StompConnection()
#         self.rconn.subscribe(self.destination)

class TestsSendReceiveBinary4(TestsSendReceiveBinary):
    def setUp(self):
        self.destination = '/topic/TEST'
        # flush queue
        get_messages(self.destination)
        self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
        self.wconn = StompConnection()


class TestsSendReceiveBinary4Queue(TestsSendReceiveBinary):
    def setUp(self):
        self.destination = '/queue/TEST/F'
        self.rconn = StompConnection()
        self.rconn.subscribe(self.destination)
        self.wconn = StompConnection()
    
    def tearDown(self):
        self.rconn.close()
        self.wconn.close()
        # flush queue
        get_messages(self.destination)


# TODO: add tests for receive_message, receive_bytes, get_message_bodies,
# get_messages(maxmessages)

if __name__ == '__main__':
    # flush queues
    for part in ('', '/A', '/B', '/C', '/D', '/E', '/F'):
        get_messages('/queue/TEST%s' % part)
    unittest.main()
    # flush queues
    for part in ('', '/A', '/B', '/C', '/D', '/E', '/F'):
        get_messages('/queue/TEST%s' % part)

