### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: editannotationnotify.py 49794 2008-01-29 22:48:06Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49794 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

                
class EditAnnotationNotify(object) :
    def changed(self) :
        notify(ObjectModifiedEvent(self.context))            
    
                    
