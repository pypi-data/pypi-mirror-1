"""perforce.tests.objects - Test the object-oriented Perforce classes.
"""

import os
import unittest
import perforce
import perforce.connection
from perforce.tests.server import PerforceServerMixin

class ClientTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      unittest.TestCase.__init__(self, *args, **kwargs)
      PerforceServerMixin.__init__(self)

    def testFetchClient(self):
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                from perforce import Client
                client = Client(p4, p4.client)
                self.assertEqual(client['Client'], p4.client)
            except perforce.CommandError:
                self.fail("Could not fetch client '%s'" % p4.client)
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testClientOptions(self):
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                from perforce import Client
                client = Client(p4, p4.client)

                options = ['locked', 'rmdir', 'modtime',
                           'allwrite', 'clobber', 'compress']

                # Check that we can query the value of the options
                for opt in options:
                    val = client[opt]

                # Check that we can set the value of the options
                for opt in options:
                    client[opt] = False
                    self.failIf(client[opt])

                    client[opt] = True
                    self.failUnless(client[opt])

                    client[opt] = True
                    self.failUnless(client[opt])

                    client[opt] = False
                    self.failIf(client[opt])

            except perforce.CommandError:
                self.fail("Could not fetch client '%s'" % p4.client)
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testClientProperties(self):
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                from perforce import Client
                client = Client(p4, p4.client)
                
                # Fields current as of 2005.2
                val = client['Client']
                val = client['Access']
                val = client['Update']
                val = client['Owner']
                val = client['Host']
                val = client['Root']
                val = client['Description']                
                val = client['AltRoots']
                val = client['Options']
                val = client['LineEnd']
                val = client['View']

                client['Client'] = 'test-client'
                self.assertEqual(client['Client'], 'test-client')
                
                client['Root'] = os.getcwd()
                self.assertEqual(client['Root'], os.getcwd())
                
                client['AltRoots'] = []
                self.assertEqual(client['AltRoots'], [])

                client['Description'] = "test client"
                self.assertEqual(client['Description'], "test client")
                
                client['Owner'] = 'testuser'
                self.assertEqual(client['Owner'], 'testuser')
                
                client['Host'] = 'localhost'
                self.assertEqual(client['Host'], 'localhost')

                client['LineEnd'] = 'share'
                self.assertEqual(client['LineEnd'], 'share')

                client['View'] = [('//depot/foo/...',
                                   '//test-client/...')]
                self.assertEqual(client['View'],
                                 [('//depot/foo/...',
                                   '//test-client/...')])

                client['View'].append(('//depot/bar/...',
                                       '//test-client/bar/...'))
                self.assertEqual(client['View'],
                                 [('//depot/foo/...',
                                   '//test-client/...'),
                                  ('//depot/bar/...',
                                   '//test-client/bar/...')])

            except perforce.CommandError:
                self.fail("Could not fetch client '%s'" % p4.client)
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

class LabelTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      unittest.TestCase.__init__(self, *args, **kwargs)
      PerforceServerMixin.__init__(self)

    def testFetchLabel(self):
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                from perforce import Label
                label = Label(p4, 'test-label')
                self.assertEqual('test-label', label['Label'])
            except perforce.CommandError:
                self.fail("Could not fetch label 'test-label'")
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testLabelProperties(self):
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                from perforce import Label
                label = Label(p4, 'test-label')

                val = label['Label']
                val = label['Update']
                val = label['Access']
                val = label['Owner']
                val = label['Description']
                val = label['Options']
                val = label['View']
                val = label['locked']

                label['Label'] = 'my-test-label'
                self.assertEqual(label['Label'], 'my-test-label')
                
                label['Owner'] = 'testuser'
                self.assertEqual(label['Owner'], 'testuser')

                desc = """This label is used for testing.

It contains useful things.
"""
                label['Description'] = desc
                self.assertEqual(label['Description'], desc)

                label['locked'] = True
                self.failUnless(label['locked'])

                label['locked'] = True
                self.failUnless(label['locked'])

                label['locked'] = False
                self.failIf(label['locked'])

                label['locked'] = False
                self.failIf(label['locked'])

                label['locked'] = True
                self.failUnless(label['locked'])

                label['View'] = ["//depot/pathA/...",
                                 "//depot/pathB/..."]
                self.assertEqual(label['View'], ["//depot/pathA/...",
                                                 "//depot/pathB/..."])
                
            except perforce.CommandError:
                self.fail("Could not fetch label 'test-label'")
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

class UserTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      unittest.TestCase.__init__(self, *args, **kwargs)
      PerforceServerMixin.__init__(self)

    def testSetPassword(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                try:
                    from perforce import User
                    user = User(p4, p4.user)
                    
                    try:
                        user.setPassword(oldPassword='',
                                         newPassword='secret')
                    except perforce.CommandError:
                        self.fail("Could not set password to 'secret'")
                        
                    try:
                        user.setPassword(oldPassword='secret',
                                         newPassword='supersecret')
                    except perforce.CommandError:
                        self.fail("Could not set password to 'supersecret'")
                except perforce.CommandError:
                    self.fail("Could not fetch user form")
            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testUpdateEmail(self):
        
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                try:
                    from perforce import User
                    user = User(p4, p4.user)
                    user['Email'] = 'test@example.com'
                    try:
                        user.save()
                    except perforce.CommandError:
                        self.fail("Could not update email address")

                    user = User(p4, p4.user)
                    self.assertEqual(user['Email'], 'test@example.com')

                except perforce.CommandError:
                    self.fail("Could not fetch user form")
            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

class ChangeTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        PerforceServerMixin.__init__(self)

    def setUp(self):
        # Start the Perforce server
        PerforceServerMixin.setUp(self)

        # Create a client to use
        import tempfile
        self.clientRoot = tempfile.mkdtemp()

        p4 = perforce.connection.Connection()
        p4.port = self.port
        p4.connect()

        from perforce import Client
        client = Client(p4, 'test-client')
        client['Description'] = 'A test client.'
        client['Root'] = self.clientRoot
        client['View'] = [('//depot/...', '//test-client/...')]
        client.save()
        self.client = client

    def tearDown(self):
        try:
            try:
                # Delete the client from Perforce
                client = self.client
                del self.client
                client.delete()
            finally:
                # Recursively delete all contents of the temp directory
                rootDir = self.clientRoot
                del self.clientRoot
                for root, dirs, files in os.walk(rootDir, topdown=False):
                    for name in files:
                        path = os.path.join(root, name)
                        if not os.access(path, os.W_OK):
                            os.chmod(path, 0777)
                        os.remove(path)
                    for name in dirs:
                        path = os.path.join(root, name)
                        if not os.access(path, os.W_OK):
                            os.chmod(path, 0777)
                        os.rmdir(path)
                os.rmdir(rootDir)
        finally:
            # Shut down the Perforce server
            PerforceServerMixin.tearDown(self)

    def testSaveNewChangelist(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            p4.client = self.client['Client']
            try:
                from perforce import Change
                change = Change(p4)

                self.assertEqual(change['Change'], 'new')

                change['Description'] = "A new, empty changelist."
                change.save()

                change.refresh()
                self.failUnless(change['Change'].isdigit())
            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testSaveNewChangelistOnNamedClient(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()

            # Set to something different
            p4.client = 'other-client'
            
            try:
                from perforce import Change
                change = Change(p4, client=self.client['Client'])

                self.assertEqual(change['Change'], 'new')
                self.assertEqual(change['Client'], self.client['Client'])

                change['Description'] = "A new, empty changelist."
                change.save()

                change.refresh()
                self.failUnless(change['Change'].isdigit())
                self.assertEqual(change['Client'], self.client['Client'])
            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testUpdateExistingChangelist(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            p4.client = self.client['Client']
            try:
                from perforce import Change
                change = Change(p4)
                change['Description'] = "A new, empty changelist."
                change.save()
                
                change.refresh()
                self.assertEqual(change['Description'],
                                 "A new, empty changelist.\n")

                change['Description'] = "Some multi-line description\n" + \
                                        "of the change list."
                change.save()
                
                change.refresh()
                self.assertEqual(change['Description'],
                                 "Some multi-line description\n" +
                                 "of the change list.\n")
            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testSubmitDefaultChangelist(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            p4.client = self.client['Client']
            try:
                f = file(os.path.join(self.clientRoot, 'foo.txt'), 'wb')
                try:
                    f.write('Some random text.\n')
                    f.write('This file is under revision control.\n')
                finally:
                    f.close()

                p4.run('add', '//%s/foo.txt' % p4.client)
                
                from perforce import Change
                change = Change(p4)

                self.assertEqual(change['Files'],
                                 ['//depot/foo.txt'])
                
                change['Description'] = "Added foo.txt"
                change.submit()

                change.refresh()
                self.failUnless(change['Change'].isdigit())
                self.assertEqual(change['Status'], 'submitted')

            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testSubmitDefaultChangelistOnNamedClient(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            p4.client = self.client['Client']
            try:
                f = file(os.path.join(self.clientRoot, 'foo.txt'), 'wb')
                try:
                    f.write('Some random text.\n')
                    f.write('This file is under revision control.\n')
                finally:
                    f.close()

                p4.run('add', '//%s/foo.txt' % p4.client)

                p4.client = 'other-client'
                
                from perforce import Change
                change = Change(p4, client=self.client['Client'])

                self.assertEqual(change['Files'],
                                 ['//depot/foo.txt'])
                
                change['Description'] = "Added foo.txt"
                change.submit()

                change.refresh()
                self.failUnless(change['Change'].isdigit())
                self.assertEqual(change['Status'], 'submitted')
                self.assertEqual(change['Client'], self.client['Client'])

            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)

    def testSubmitNamedChangelist(self):
        
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            p4.client = self.client['Client']
            try:
                f = file(os.path.join(self.clientRoot, 'foo.txt'), 'wb')
                try:
                    f.write('Some random text.\n')
                    f.write('This file is under revision control.\n')
                finally:
                    f.close()

                p4.run('add', '//%s/foo.txt' % p4.client)
                
                from perforce import Change
                change = Change(p4)

                self.assertEqual(change['Files'],
                                 ['//depot/foo.txt'])
                
                change['Description'] = "Added foo.txt"
                change.save()

                change.refresh()
                self.failUnless(change['Change'].isdigit())
                self.assertEqual(change['Status'], 'pending')

                change.submit()

                change.refresh()
                self.failUnless(change['Change'].isdigit())
                self.assertEqual(change['Status'], 'submitted')

            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)
        
    def testChangelistRenamedOnSubmit(self):
        
        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            p4.client = self.client['Client']
            try:
                from perforce import Change
                change1 = Change(p4)
                change1['Description'] = "The first change."
                change1.save()

                change2 = Change(p4)
                change2['Description'] = "The second change."
                change2.save()

                change1.refresh()
                change2.refresh()
                self.assertEqual(change1['Change'], '1')
                self.assertEqual(change2['Change'], '2')
                
                f = file(os.path.join(self.clientRoot, 'foo.txt'), 'wb')
                try:
                    f.write('Some random text.\n')
                    f.write('This file is under revision control.\n')
                finally:
                    f.close()

                p4.run('add', '-c', '1', '//%s/foo.txt' % p4.client)
                
                change1.refresh()
                self.assertEqual(change1['Files'],
                                 ['//depot/foo.txt'])
                change1.submit()

                change1.refresh()
                self.assertEqual(change1['Change'], '3')

            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)
        
class CounterTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        PerforceServerMixin.__init__(self)

    def testGetSetCounter(self):

        p4 = perforce.connection.Connection()
        p4.port = self.port
        try:
            p4.connect()
            try:
                from perforce.objects import Counter

                # Try a custom counter
                foo = Counter(p4, 'foo')
                self.assertEqual(foo.getValue(), 0)
                foo.setValue(100)
                self.assertEqual(foo.getValue(), 100)
                foo.setValue('123')
                self.assertEqual(foo.getValue(), 123)
                foo.setValue(u'234')
                self.assertEqual(foo.getValue(), 234)

                # Try a protected counter
                change = Counter(p4, 'change')
                self.assertEqual(change.getValue(), 0)
                self.assertRaises(perforce.objects.CommandError,
                                  change.setValue, 3)
                change.setValue(3, force=True)
                self.assertEqual(change.getValue(), 3)
            finally:
                p4.disconnect()
        except perforce.connection.ConnectionFailed:
            self.fail("Could not connect to server '%s'" % p4.port)
