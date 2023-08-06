### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The SimpleVocabulary class work arround of unicode bug: this class
can work this national language utf-8 strings.

$Id: simplevocabulary.py 51828 2008-10-08 08:45:35Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51828 $"
 
from zope.interface import implements
from zope.schema import vocabulary
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleTerm

class SimpleVocabulary(vocabulary.SimpleVocabulary) :

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        try:
            return self.by_token[str(token)]
        except KeyError:
            raise LookupError(token)

