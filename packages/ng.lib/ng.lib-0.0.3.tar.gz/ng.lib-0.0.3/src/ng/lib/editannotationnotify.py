### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: editannotationnotify.py 49608 2008-01-21 12:27:38Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49608 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

                
class EditAnnotationNotify(object) :
    def changed(self) :
        notify(ObjectModifiedEvent(self.context))            
    
                    
