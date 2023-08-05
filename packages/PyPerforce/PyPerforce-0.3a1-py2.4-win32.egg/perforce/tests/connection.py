"""perforce.tests.connection - Tests for the perforce.connection module.
"""

import sys
import unittest
import protocols
import perforce.connection
from perforce.tests.server import PerforceServerMixin

class ConnectionTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      unittest.TestCase.__init__(self, *args, **kwargs)
      PerforceServerMixin.__init__(self)

    def testSetPropertiesOnInit(self):

        p = perforce.connection.Connection(port=self.port)
        self.assertEqual(p.port, self.port)
        
        p = perforce.connection.Connection(user='test')
        self.assertEqual(p.user, 'test')
        
        p = perforce.connection.Connection(host='hostname')
        self.assertEqual(p.host, 'hostname')

        p = perforce.connection.Connection(charset='utf8')
        self.assertEqual(p.charset, 'utf8')

        from perforce.api import CharSet
        p = perforce.connection.Connection(charset=CharSet.NOCONV)
        self.assertEqual(p.charset, str(CharSet.NOCONV))

        p = perforce.connection.Connection(password='secret')
        self.assertEqual(p.password, 'secret')

        from os.path import join
        from os import getcwd
        p = perforce.connection.Connection(cwd=join(getcwd(), 'test'))
        self.assertEqual(p.cwd, join(getcwd(), 'test'))

        p = perforce.connection.Connection(language='chinese')
        self.assertEqual(p.language, 'chinese')

        p = perforce.connection.Connection(client='my-client')
        self.assertEqual(p.client, 'my-client')

        # Test multiple parameters at the same time
        p = perforce.connection.Connection(port=self.port,
                                           user='test',
                                           password='secret',
                                           client='my-client',
                                           charset='none')
        self.assertEqual(p.port, self.port)
        self.assertEqual(p.user, 'test')
        self.assertEqual(p.password, 'secret')
        self.assertEqual(p.client, 'my-client')
        self.assertEqual(p.charset, 'none')

    def testGetSetProperties(self):

        p = perforce.connection.Connection()

        p.user = 'test'
        self.assertEqual(p.user, 'test')

        p.charset = 'utf8'
        self.assertEqual(p.charset, 'utf8')

        from os.path import join

        testCwd = join(p.cwd, 'test')
        p.cwd = testCwd
        self.assertEqual(p.cwd, testCwd)

        p.port = 'perforce:12345'
        self.assertEqual(p.port, 'perforce:12345')

        p.host = 'localhost'
        self.assertEqual(p.host, 'localhost')

        # TODO: Add more supported o/s identifiers here
        platforms = {'win32' : 'NT',
                     'cygwin' : 'UNIX',
                     'linux2' : 'UNIX'}
        self.assertEqual(p.os, platforms[sys.platform])

        p.client = 'test-client'
        self.assertEqual(p.client, 'test-client')

        p.password = 'secret'
        self.assertEqual(p.password, 'secret')

    def testConnectDisconnect(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port

        try:
            p4.connect()
            
            try:
                results = p4.run('info')
            except perforce.connection.ConnectionDropped:
                self.fail("Connection dropped running 'p4 info'")

            p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testConnectWithProgramInfo(self):

        import perforce

        p4 = perforce.connection.Connection()
        p4.port = self.port

        ver = perforce.__version__

        try:
            p4.connect(prog='PyPerforce', version=ver)
            p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testRunMultipleCommands(self):
        p4 = perforce.connection.Connection()
        p4.port = self.port
        
        try:
            p4.connect()
            try:
                for i in xrange(50):
                    results = p4.run('info')
            except perforce.connection.ConnectionDropped:
                self.fail("Connection dropped running 'p4 info'")
            p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testFetchClient(self):
        p4 = perforce.connection.Connection()
        p4.port = self.port
        
        try:
            p4.connect()
            try:
                results = p4.run('client', '-o')
                if results.errors:
                    self.fail("Failed to fetch client '%s'" % p4.client)
                    
                form = results.forms[0]
                self.assertEqual(form['Client'], p4.client)
            except perforce.connection.ConnectionDropped:
                self.fail("Connection dropped running 'p4 client -o'")
            p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testRunCommandWithIOutputConsumer(self):

        import perforce.results

        class P4InfoConsumer(object):
            protocols.advise(
                instancesProvide=[perforce.results.IOutputConsumer]
                )

            def __init__(self):
                self.isFinished = False
                self.messages = []
                self.records = []

            def outputMessage(self, message):
                self.messages.append(message)

            def outputRecord(self, record):
                self.records.append(record)

            def outputText(self, data):
                pass

            def outputBinary(self, data):
                pass

            def outputForm(self, form):
                pass
            
            def finished(self):
                self.isFinished = True
                
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()

            consumer = P4InfoConsumer()
            try:
                results = p4.run('info', output=consumer)
                
                self.failUnless(results is consumer)
                self.failUnless(consumer.isFinished)
                self.failUnless(consumer.messages or consumer.records)
                
            except perforce.connection.ConnectionDropped:
                self.fail("Connection dropped running 'p4 info'")

            p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testRunCommandWithClientUser(self):

        import perforce.api

        class P4InfoClientUser(perforce.api.ClientUser):

            def __init__(self):
                self.isFinished = False
                self.messages = []
                self.records = []

            def message(self, message):
                self.messages.append(message)

            def outputStat(self, data):
                self.records.append(data)

            def finished(self):
                self.isFinished = True
                
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()

            clientUser = P4InfoClientUser()
            try:
                results = p4.run('info', ui=clientUser)
                
                self.failUnless(results is clientUser)
                self.failUnless(clientUser.isFinished)
                self.failUnless(clientUser.messages or clientUser.records)
                
            except perforce.connection.ConnectionDropped:
                self.fail("Connection dropped running 'p4 info'")

            p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)


class UnicodeConnectionTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      unittest.TestCase.__init__(self, *args, **kwargs)
      PerforceServerMixin.__init__(self, unicodeMode=True)

    def testGetSetProperties(self):

        p = perforce.connection.Connection()
        p.charset = 'utf8'

        p.user = 'test'
        self.assertEqual(p.user, u'test')
        self.failUnless(isinstance(p.user, unicode))

        p.user = u'test\u20AC'
        self.assertEqual(p.user, u'test\u20AC')
        self.failUnless(isinstance(p.user, unicode))

        from os.path import join

        testCwd = join(p.cwd, 'test')
        p.cwd = testCwd
        self.assertEqual(p.cwd, testCwd)

        p.port = 'perforce:12345'
        self.assertEqual(p.port, 'perforce:12345')
        self.failUnless(isinstance(p.port, str))

        p.host = 'localhost'
        self.assertEqual(p.host, 'localhost')
        self.failUnless(isinstance(p.host, str))

        # TODO: Add more supported o/s identifiers here
        platforms = {'win32' : 'NT',
                     'cygwin' : 'UNIX',
                     'linux2' : 'UNIX'}
        self.assertEqual(p.os, platforms[sys.platform])
        self.failUnless(isinstance(p.os, str))

        p.client = 'test-client'
        self.assertEqual(p.client, 'test-client')
        self.failUnless(isinstance(p.client, unicode))

        p.client = u'test-client\u20AC'
        self.assertEqual(p.client, u'test-client\u20AC')
        self.failUnless(isinstance(p.client, unicode))

        p.password = u'secret-squirrel'
        self.assertEqual(p.password, 'secret-squirrel')
        self.failUnless(isinstance(p.client, unicode))
