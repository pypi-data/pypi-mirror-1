import unittest, doctest

from zope.testing import doctestunit
from zope.component import testing

class DummyEntry(object):

    def __init__(self, id=None):
        self.id = id

    def getId(self):
        return self.id

def test_suite():
    return unittest.TestSuite([

        # Unit tests for your API
        doctestunit.DocFileSuite(
            'README.txt',
            package='bibliograph.core',
            setUp=testing.setUp,
            tearDown=testing.tearDown),
            
        doctestunit.DocTestSuite(
            'bibliograph.core.utils',
            optionflags=doctest.ELLIPSIS,
            globs=dict(DummyEntry=DummyEntry))
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
