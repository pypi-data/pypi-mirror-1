### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class for all viewlet in contentlet page.

$Id: viewletbase.py 52413 2009-01-30 12:47:23Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 52413 $"

from zope.interface import Interface, implements
from interfaces import IOrderInformation
from zope.app.zapi import getMultiAdapter
from zope.component import ComponentLookupError

class ViewletBase(object) :
    order = 0
    __name__ = ""

    def __init__(self,context,request,something,master,*kv,**kw) :
        self.context = context
        self.request = request
        self.master = master
        self.order = int(str(self.order))
        super(ViewletBase,self).__init__(context,request,something,master,*kv,**kw)
    
    def __cmp__(self,ob) :
        try :
            dict = getMultiAdapter([self.master,self.request],IOrderInformation).dict
            return cmp(dict[self.__name__], dict[ob.__name__])
        except (KeyError,ComponentLookupError) :
            return cmp(self.order,ob.order)

        