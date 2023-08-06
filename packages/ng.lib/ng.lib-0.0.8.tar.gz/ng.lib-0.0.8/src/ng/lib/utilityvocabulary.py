### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Utility vocabulary

$Id: utilityvocabulary.py 53229 2009-06-11 07:49:25Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53229 $"

from zope.interface import implements, alsoProvides
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import  IContextSourceBinder, ITextLine
from zope.app.zapi import getUtilitiesFor

class UtilityVocabulary(object) :
    implements(IContextSourceBinder)
        
    def __init__(self,iface) :
        self.iface = iface        
        
    def __call__(self, ob) :
        vocabulary = SimpleVocabulary.fromValues(
            sorted([ x for x,y in getUtilitiesFor(self.iface,context=ob)])
        )
        alsoProvides(vocabulary,ITextLine)
        return vocabulary
