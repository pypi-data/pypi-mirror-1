### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: editannotationnotify.py 50112 2008-01-16 10:27:14Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 50112 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

                
class EditAnnotationNotify(object) :
    def changed(self) :
        notify(ObjectModifiedEvent(self.context))            
    
                    
