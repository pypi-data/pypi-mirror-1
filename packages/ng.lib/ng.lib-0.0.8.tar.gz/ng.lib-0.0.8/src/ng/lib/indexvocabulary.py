### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Vocabulary for value from search indexes.

$Id: indexvocabulary.py 53103 2009-05-21 12:18:48Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53103 $"

from zope.app.zapi import getUtility
from zope.interface import implements
from zope.schema.interfaces import  IContextSourceBinder
from zc.catalog.interfaces import IIndexValues
from zope.interface import implements, alsoProvides
from simplevocabulary import SimpleVocabulary

class IndexVocabulary(object) :
    implements(IContextSourceBinder)

    def __init__(self,name) :
        self.name = name
        
    def __call__(self,context) :
        vocabulary = SimpleVocabulary.fromValues(
          [ x for x in sorted(
                getUtility(IIndexValues,context=context,name=self.name).values()
                ) 
            ]
          ) 
        return vocabulary

