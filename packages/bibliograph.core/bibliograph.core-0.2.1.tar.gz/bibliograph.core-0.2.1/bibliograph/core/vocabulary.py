# -*- coding: utf-8 -*-
###############################################################################
# $Copy$
###############################################################################
""" Vocabularies used by the bibliograph.* packages

$Id$
"""
__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

# Zope imports
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary

from zope.app.schema.vocabulary import IVocabularyFactory

# XXX as long as we don't have a propper translation messagefactory
_ = unicode

###############################################################################

class BibFormatVocabulary(object):
    """ A vocabulary for bibliographic formats
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        """ A simple constant vocabulary """
        return SimpleVocabulary.fromItems([
            (_("Bibtex"), 'bibtex'),
            (_("Endnote"), 'endnote'),
            (_("RIS"), 'ris'),
            (_("XML (MODS)"), 'xml'),
            (_("PDF"), 'pdf'),
        ])

BibFormatVocabularyFactory = BibFormatVocabulary()