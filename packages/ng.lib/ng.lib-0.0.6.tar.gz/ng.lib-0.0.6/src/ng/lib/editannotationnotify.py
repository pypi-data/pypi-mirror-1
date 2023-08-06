### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: editannotationnotify.py 51828 2008-10-08 08:45:35Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 51828 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

                
class EditAnnotationNotify(object) :
    def changed(self) :
        notify(ObjectModifiedEvent(self.context))            
    
                    
