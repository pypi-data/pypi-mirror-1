"""perforce.tests - Python Perforce API unit tests
"""

__all__ = ['api', 'connection', 'forms', 'objects', 'testSuite']

def testSuite():
    """Returns a unittest.TestSuite object containing all unit tests.

    Tests the entire 'perforce' package.
    """

    # Import the unittest module
    import unittest

    # Import our test case modules
    import perforce.tests.api
    import perforce.tests.forms
    import perforce.tests.connection
    import perforce.tests.objects

    # Load all test cases into a test suite
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromModule(perforce.tests.api))
    suite.addTest(loader.loadTestsFromModule(perforce.tests.forms))
    suite.addTest(loader.loadTestsFromModule(perforce.tests.connection))
    suite.addTest(loader.loadTestsFromModule(perforce.tests.objects))
    return suite
