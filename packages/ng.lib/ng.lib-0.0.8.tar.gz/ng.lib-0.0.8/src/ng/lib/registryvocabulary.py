### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Registry vocabulary

$Id: registryvocabulary.py 53271 2009-06-13 14:14:34Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53271 $"

from zope.interface import implements, alsoProvides
from ng.lib.simplevocabulary import SimpleVocabulary
from zope.schema.interfaces import  IContextSourceBinder, ITextLine
from zope.app.zapi import getUtilitiesFor
from ng.app.registry.interfaces import IRegistry

class RegistryVocabulary(object) :
    implements(IContextSourceBinder)
        
    def __init__(self,name,default=[]) :
        self.name = name
        self.default = default
        
    def __call__(self, ob) :
        text = IRegistry(ob).param(self.name,None)
        if text is None :
            keys = self.default            
        else :
            keys = [ x.strip() for x in text.split("\n") if x]
        
        vocabulary = SimpleVocabulary.fromValues(sorted(keys))
        alsoProvides(vocabulary,ITextLine)
        return vocabulary
