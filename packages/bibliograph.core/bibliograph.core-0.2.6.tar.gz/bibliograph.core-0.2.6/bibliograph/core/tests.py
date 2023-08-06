import unittest, doctest

from zope.testing import doctestunit
from zope.component import testing
from zope.component import provideUtility
from zope.component import getUtility

from zope.app.schema.vocabulary import IVocabularyFactory

from bibliograph.core.vocabulary import BibFormatVocabularyFactory

class DummyEntry(object):

    def __init__(self, id=None):
        self.id = id

    def getId(self):
        return self.id

class VocabularyTestCase(unittest.TestCase):

    def setUp(self):
        provideUtility(BibFormatVocabularyFactory,
                       IVocabularyFactory,
                       u'bibliography.formats')

    def test_formatsvoc(self):
        voc = getUtility(IVocabularyFactory, u'bibliography.formats')(object())
        assert 'bibtex' in voc


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
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            globs=dict(DummyEntry=DummyEntry)),

        unittest.makeSuite(VocabularyTestCase),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
